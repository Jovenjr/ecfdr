from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in csf_do/__init__.py
from csf_do import __version__ as version

setup(
	name="csf_do",
	version=version,
	description="Country Specific Functionality for Dominican Republic",
	author="Navari Limited (Original Author), Refactored for Dominican Republic",
	author_email="info@navari.co.ke",
	# Only package the Dominican app to avoid installing legacy Kenya modules
	packages=find_packages(include=["csf_do", "csf_do.*"]),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
