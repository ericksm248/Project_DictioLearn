from setuptools import setup, find_packages

setup(
    name="DictioLearn",
    version="1.6",
    description="Proyecto de interfaz gráfica con PyQt5 para aprender y memorizar nuevas palabras en ingles",
    author="Ericsón Vilcahuamán",
    author_email="vilca.elec@gmail.com",
    packages=find_packages(),  
    include_package_data=True, 
    install_requires=[
        "PyQt5>=5.15", 
        "pyttsx3>=2.98",
    ],
    entry_points={
        'console_scripts': [
            'dictiolearn = MyApp.main:main',  # Script ejecutable desde consola
        ],
    },
)