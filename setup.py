from setuptools import setup, find_packages

setup(
    name='oracle',
    version='0.0.1',
    description='LLM App',
    long_description="LLM App",
    long_description_content_type="text/markdown",
    url='github.com',
    author='olivier',
    author_email='ducrouxolivier@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        'accelerate',
        'torch',
        'llama-index',
        'flask-socketio',
        'flask',
        'ipdb',
        'transformers',
        'huggingface-hub',
        'beautifulsoup4',
        'paramiko'
    ],
)
