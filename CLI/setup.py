from setuptools import setup

setup(
    name='poi-harvester',
    version='1.1',
    description='A tool to fetch and export POI data from OpenStreetMap via Overpass API',
    author='Luca-Pascal Junge',
    author_email='lucapascal2402@gmail.com',
    url='https://github.com/lpj-app/poi-harvester',
    license='MIT',
    packages=['poi_harvester'],
    install_requires=[
        'requests>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'poi-harvester=poi_harvester.main_cli:main',
        ],
    },
)
