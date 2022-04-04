from setuptools import setup, find_packages

long_description = "hovercal uses holoviews to create customizable plots from pandas timeseries data. Panel is used to create a global heatmap and arrange the plots. The user input is a dataframe containing dates and values. The package includes a cleaning function for plotting directly from spotify json extended listening history."

setup(
    name="hovercal",
    version="0.1.0",
    description="hovercal is a package for visualizing data on a calendar heatmap",
    url="https://github.com/lianamerk/hovercal",
    long_description=long_description,
    license="MIT",
    author='Liana Merk',
    author_email='liana.merk@gmail.com',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['numpy','pandas', 'bokeh','holoviews','panel'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ]
)