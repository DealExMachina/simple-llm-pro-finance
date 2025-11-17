# Analyse : Pourquoi les Tool Calls ne Fonctionnent Pas

## 🔍 Problème Identifié

L'API Hugging Face Space **ne supporte PAS les tool calls** dans son implémentation actuelle.

## 📋 Analyse du Code

### 1. Modèle de Requête (`app/models/openai.py`)

```python
class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    # ❌ PAS de champ "tools"
    # ❌ PAS de champ "tool_choice"
```

**Problème :** Le modèle Pydantic ne définit pas les champs `tools` et `tool_choice`, donc même si PydanticAI les envoie, ils sont **ignorés** par FastAPI.

### 2. Modèle de Réponse (`app/models/openai.py`)

```python
class ChoiceMessage(BaseModel):
    role: Literal["assistant"]
    content: Optional[str] = None
    # ❌ PAS de champ "tool_calls"
```

**Problème :** Le modèle de réponse ne définit pas le champ `tool_calls`, donc même si le modèle générait des tool calls, ils ne seraient **pas retournés** dans la réponse.

### 3. Provider Transformers (`app/providers/transformers_provider.py`)

```python
async def chat(self, payload: Dict[str, Any], stream: bool = False):
    messages = payload.get("messages", [])
    temperature = payload.get("temperature", DEFAULT_TEMPERATURE)
    max_tokens = payload.get("max_tokens", DEFAULT_MAX_TOKENS)
    top_p = payload.get("top_p", DEFAULT_TOP_P)
    # ❌ PAS d'extraction de "tools"
    # ❌ PAS d'extraction de "tool_choice"
    
    # Génère juste du texte
    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    return {
        "choices": [{
            "message": {"role": "assistant", "content": generated_text},
            # ❌ PAS de "tool_calls"
        }]
    }
```

**Problème :** Le provider :
1. N'extrait pas `tools` du payload
2. Ne passe pas les tools au modèle
3. Ne parse pas les tool calls de la réponse
4. Ne retourne pas de `tool_calls` dans la réponse

## 🔄 Flux Actuel

```
PydanticAI Agent
    ↓ (envoie tools dans la requête)
FastAPI Router
    ↓ (parse avec ChatCompletionRequest - IGNORE tools)
TransformersProvider
    ↓ (n'extrait pas tools du payload)
Qwen 8B Model
    ↓ (génère du texte, pas de tool calls)
TransformersProvider
    ↓ (retourne juste content, pas tool_calls)
FastAPI Router
    ↓ (retourne ChoiceMessage sans tool_calls)
PydanticAI Agent
    ↓ (reçoit tool_calls = [])
```

## ✅ Solution : Ajouter le Support des Tool Calls

### Étape 1 : Mettre à Jour le Modèle de Requête

```python
# app/models/openai.py

from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field

class Function(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]

class Tool(BaseModel):
    type: Literal["function"] = "function"
    function: Function

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    tools: Optional[List[Tool]] = None  # ✅ AJOUTER
    tool_choice: Optional[Union[Literal["none", "auto"], Dict[str, Any]]] = None  # ✅ AJOUTER
```

### Étape 2 : Mettre à Jour le Modèle de Réponse

```python
# app/models/openai.py

class FunctionCall(BaseModel):
    name: str
    arguments: str  # JSON string

class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: FunctionCall

class ChoiceMessage(BaseModel):
    role: Literal["assistant"]
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None  # ✅ AJOUTER
```

### Étape 3 : Mettre à Jour le Provider

Le provider doit :

1. **Extraire les tools du payload**
2. **Inclure les tools dans le prompt** (format spécial pour Qwen)
3. **Parser la réponse** pour détecter les tool calls
4. **Retourner les tool calls** dans la réponse

**Option A : Format Textuel (Plus Simple)**

Si le modèle génère des tool calls en texte, parser la réponse :

```python
def _parse_tool_calls(self, generated_text: str, tools: List[Tool]) -> List[ToolCall]:
    """Parse tool calls from generated text."""
    # Chercher des patterns comme:
    # <tool_call>
    # {"name": "calculer_valeur_future", "arguments": "{\"capital_initial\": 10000}"}
    # </tool_call>
    import re
    import json
    
    tool_calls = []
    pattern = r'<tool_call>\s*({.*?})\s*</tool_call>'
    matches = re.findall(pattern, generated_text, re.DOTALL)
    
    for i, match in enumerate(matches):
        try:
            call_data = json.loads(match)
            tool_calls.append(ToolCall(
                id=f"call_{i}",
                type="function",
                function=FunctionCall(
                    name=call_data["name"],
                    arguments=json.dumps(call_data.get("arguments", {}))
                )
            ))
        except Exception as e:
            logger.warning(f"Failed to parse tool call: {e}")
    
    return tool_calls
```

**Option B : Format JSON Structured Output**

Si le modèle supporte le JSON mode, forcer un format structuré :

```python
# Dans le prompt, ajouter:
# "You must respond in JSON format with tool_calls array"
# Puis parser le JSON
```

### Étape 4 : Mettre à Jour le Router

Le router doit passer les tools au provider :

```python
# app/routers/openai_api.py

payload: Dict[str, Any] = {
    "model": body.model or settings.model,
    "messages": [m.model_dump() for m in body.messages],
    "temperature": body.temperature or 0.7,
    "top_p": body.top_p or 1.0,
    "stream": body.stream or False,
}

# ✅ AJOUTER
if body.tools:
    payload["tools"] = [t.model_dump() for t in body.tools]
if body.tool_choice:
    payload["tool_choice"] = body.tool_choice
```

## 🎯 Stratégie de Mise en Œuvre

### Phase 1 : Support Basique (Textuel)

1. ✅ Ajouter `tools` et `tool_choice` au modèle de requête
2. ✅ Ajouter `tool_calls` au modèle de réponse
3. ✅ Parser les tool calls depuis le texte généré
4. ✅ Retourner les tool calls dans la réponse

### Phase 2 : Support Avancé (Structured Output)

1. 🔄 Forcer le modèle à générer du JSON structuré
2. 🔄 Parser le JSON pour extraire les tool calls
3. 🔄 Valider les tool calls contre les tools fournis

### Phase 3 : Support Complet (Native)

1. 🎯 Fine-tuner le modèle pour générer des tool calls natifs
2. 🎯 Utiliser un format de sortie spécialisé
3. 🎯 Support complet du format OpenAI

## 📝 Notes Importantes

### Limitations du Modèle Qwen 8B

Le modèle Qwen 8B fine-tuné peut :
- ✅ Générer du texte qui mentionne les outils
- ❌ Ne pas générer de tool calls au format OpenAI natif
- ❌ Ne pas structurer la réponse avec `tool_calls`

### Solutions de Contournement

1. **Parser le texte** : Extraire les tool calls depuis le texte généré
2. **Format spécialisé** : Utiliser un format de prompt spécial pour forcer les tool calls
3. **Post-processing** : Analyser la réponse et exécuter les outils mentionnés

## 🔗 Fichiers à Modifier

1. `app/models/openai.py` : Ajouter `tools`, `tool_choice`, `tool_calls`
2. `app/providers/transformers_provider.py` : Gérer les tools et parser les tool calls
3. `app/routers/openai_api.py` : Passer les tools au provider
4. Tests : Ajouter des tests pour les tool calls

## 📚 Références

- [OpenAI Tool Calls Format](https://platform.openai.com/docs/guides/function-calling)
- [PydanticAI Tools Documentation](https://ai.pydantic.dev/tools/)
- [Qwen Model Documentation](https://huggingface.co/Qwen)

