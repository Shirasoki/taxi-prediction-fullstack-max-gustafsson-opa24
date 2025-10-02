from setuptools import setup
from setuptools import find_packages

# find_packages will find all the packages with __init__.py
print(find_packages())

setup(
    name="taxipred",
    version="0.0.2",
    description="this package contains taxipred app",
    author="Max Gustafsson",
    author_email="author@mail.se",
    install_requires=["streamlit", "pandas", "fastapi", "uvicorn", "ipykernel", "matplotlib", "seaborn", "scikit-learn", "pathlib", "joblib"],
    package_dir={"": "src"},
    package_data={"taxipred": ["data/*.csv"]},
    packages=find_packages(),
)
