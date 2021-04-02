import setuptools


setuptools.setup(
    name="mailerkivy",
    version="0.1.1",
    url="https://github.com/XtremeGood/MailerKivy",
    author="Vishesh Mangla",
    author_email="manglavishesh64@gmail.com",    
    python_requires='>=3.7',
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        "gui_scripts": [
            "mailer = mailer.main:main",
        ],
    },
        setup_requires="setuptools",
    install_requires=[
        "kivy>=2.0.0",
        "beautifulsoup4>=4.9.3",
        "docxtpl>=0.11.3",
        "pywin32>=300",
        "plyer>=2.0.0",
        "python-dateutil>=2.8.1",
        "cryptography>=3.4.7"
    ],
   extras_require={
        "build_for_windows":  ["pyinstaller>=4.2"],
    }
)



