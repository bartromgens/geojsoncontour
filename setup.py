from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='geojsoncontour',
    version='0.5.1',
    description='Convert matplotlib contour plots to geojson',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='contour plot geojson pyplot matplotlib gis map',
    url='http://github.com/bartromgens/geojsoncontour',
    author='Bart Römgens',
    author_email='bart.romgens@gmail.com',
    license='MIT',
    packages=['geojsoncontour', 'geojsoncontour.utilities'],
    install_requires=[
        'geojson',
        'numpy',
        'matplotlib>=3.8',
        'xarray'
    ],
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
