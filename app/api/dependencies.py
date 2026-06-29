from aiograpi import Client
from dishka import Provider, Scope, provide
from pydantic_ai import Agent
from pydantic_ai.models.xai import XaiModel
from pydantic_ai.providers.xai import XaiProvider

from app.adapters.files import Files
from app.adapters.instagram_auth import Credentials, InstagramLoginService
from app.adapters.instagram_client import (
    InstagramAuth,
    InstagramClient,
)
from app.domain.agent import (
    AgentDependencies,
    AgentService,
    follow_user,
    like_post,
    send_message,
)
from app.domain.ports import InstagramPort
from app.infrastructure.config import Settings


def provide_service() -> Provider:
    service_provider = Provider(scope=Scope.APP)
    service_provider.provide(AgentDependencies)
    service_provider.provide(AgentService)
    return service_provider


class ProvideAdapters(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    def files(self, settings: Settings) -> Files:
        return Files(settings.session_file)


class ProvideXai(Provider):
    @provide(scope=Scope.APP)
    def xai(self, settings: Settings) -> XaiProvider:
        return XaiProvider(api_key=settings.xai_api_key.get_secret_value())

    @provide(scope=Scope.APP)
    def xai_model(self, settings: Settings, xai_provider: XaiProvider) -> XaiModel:
        return XaiModel(settings.xai_model, provider=xai_provider)

    @provide(scope=Scope.APP)
    def xai_agent(self, model: XaiModel) -> Agent:
        return Agent(
            model,
            tools=[send_message, follow_user, like_post],
        )


class ProvideInstagram(Provider):
    @provide(scope=Scope.APP)
    def aiograpi(self) -> Client:
        return Client()

    @provide(scope=Scope.APP)
    def auth(self, cl: Client) -> InstagramAuth:
        return InstagramAuth(cl)

    @provide(scope=Scope.APP, provides=InstagramPort)
    def client(self, cl: Client) -> InstagramClient:
        return InstagramClient(cl)

    @provide(scope=Scope.APP)
    def login(
        self, auth: InstagramAuth, settings: Settings, files: Files
    ) -> InstagramLoginService:
        credentials = Credentials(settings.login, settings.password, settings.secret)
        return InstagramLoginService(auth, credentials, files)
