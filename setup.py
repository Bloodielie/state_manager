import setuptools


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as f:
        return f.read()


requirements = [
    "aioredis==1.3.1",
    "pydantic==1.6",
    "python-dotenv==0.14.0",
]


setuptools.setup(
    name="state_manager",
    python_requires=">=3.8",
    version="0.2.0",
    packages=setuptools.find_packages(),
    url="https://github.com/Bloodielie/state_manager",
    license="Apache-2.0 License",
    author="Bloodie_lie",
    author_email="riopro2812@gmail.com",
    description="fsm for people",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "full": [
            "vkwave==0.2.5",
            "aiogram==2.9.2",
            "ujson",
        ],
        "vk": [
            "vkwave==0.2.5",
        ],
        "telegram": [
            "aiogram==2.9.2",
        ]
    },
    include_package_data=False,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
    ],
)
