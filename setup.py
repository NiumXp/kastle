from setuptools import setup


readme = ''
with open('README.md') as f:
  readme = f.read()


setup(
  name='kastle',
  description='A web framework for Python that prioritizes simplicity.',
  packages=['kastle']
)
