from setuptools import find_packages, setup


setup(
    name="go2web",
    version="0.1.0",
    description="HTTP-over-sockets CLI fetcher and search tool",
    packages=find_packages(include=["go2web_app", "go2web_app.*"]),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "go2web=go2web_app:main",
        ]
    },
)
