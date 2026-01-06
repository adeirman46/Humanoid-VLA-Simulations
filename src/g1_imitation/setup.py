from setuptools import setup, find_packages

package_name = 'g1_imitation'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Humanoid VLA',
    maintainer_email='user@example.com',
    description='LAFAN motion capture imitation learning for Unitree G1',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'download_lafan = scripts.download_lafan:main',
            'train_deepmimic = scripts.train_deepmimic:main',
            'visualize_motion = scripts.visualize_motion:main',
        ],
    },
)
