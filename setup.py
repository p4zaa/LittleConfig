import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requires = [
    'yaml'
]

setuptools.setup(
    name='LittleConfig',
    version='0.1',
    author='p4zaa',
    author_email='pathompong.workspace@gmail.com',
    description='LittleConfig Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/p4zaa/LittleConfig',
    project_urls = {
        "Bug Tracker": "https://github.com/p4zaa/LittleConfig/issues"
    },
    license='MIT',
    packages=['LittleConfig'],
    install_requires=requires,
)