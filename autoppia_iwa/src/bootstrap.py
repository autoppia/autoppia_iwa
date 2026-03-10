from autoppia_iwa.src.di_container import DIContainer


class AppBootstrap:
    """
    In charge of initializing Dependency Injection
    """

    def __init__(self):
        self.configure_dependency_injection()

    def configure_dependency_injection(self):
        self.container = DIContainer()
