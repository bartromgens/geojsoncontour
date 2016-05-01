from setuptools import setup

setup(
    name='geojsoncontour',
    version='0.1dev',
    description='Convert matplotlib contour plots to geojson',
    url='http://github.com/bartromgens/geojsoncontour',
    author='Bart Römgens',
    author_email='bart.romgens@gmail.com',
    license='MIT',
    packages=['geojsoncontour'],
    install_requires=[
        'geojson',
        'numpy',
        'matplotlib'
    ],
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
)