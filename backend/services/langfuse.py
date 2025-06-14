import os

try:
    from langfuse import Langfuse
    
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    enabled = False
    if public_key and secret_key:
        enabled = True
        langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    else:
        # Create a dummy langfuse object if credentials are not available
        class DummyLangfuse:
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
        
        langfuse = DummyLangfuse()
except ImportError:
    # Create a dummy langfuse object if langfuse is not available
    class DummyLangfuse:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    langfuse = DummyLangfuse()
