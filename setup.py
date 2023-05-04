from setuptools import find_packages, setup


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()


readme = get_file_content("README.md")
history = get_file_content("HISTORY.rst")
version = get_file_content("version.txt").strip()

setup(
    name="cloudshell-rest-api",
    version=version,
    description="Python client for the CloudShell REST API",
    long_description=readme + "\n\n" + history,
    author="Boris Modylevsky",
    author_email="borismod@gmail.com",
    url="https://github.com/QualiSystems/cloudshell-rest-api",
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_file_content("requirements.txt"),
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="cloudshell quali sandbox cloud rest api",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="tests",
    tests_require=get_file_content("test_requirements.txt"),
    python_requires="~=3.7",
)
