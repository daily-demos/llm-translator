from services.azure_ai_service import AzureAIService
from services.mock_ai_service import MockAIService
from services.open_ai_service import OpenAIService
from services.playht_ai_service import PlayHTAIService

services = {
    "azure": AzureAIService,
    "mock": MockAIService,
    "openai": OpenAIService,
    "playht": PlayHTAIService
}
