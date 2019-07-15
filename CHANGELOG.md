# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 0.0.5 - 2019-07-15

### Added in 0.0.5

- Added KvLang as Embedded language in files with python extension
- Language server should start even when module kivy is not installed under selected python path
- Updated KvLint to work properly with .kv and .py files
- Update of language client and KvLang extension requirements

## 0.0.4 - 2019-01-23

### Added in 0.0.4

- Python path can be changed from extension status bar
- Language server will restart when valid python path is provided in settings
- Updated LS server

## 0.0.3 - 2019-01-14

### Added in 0.0.3

- Reduce LS server crashes in Python 3.x
- LS server should always start in Python 2.7
- Added new linter information: Trailing whitespace, Final newline missing, Trailing newlines, Kivy parser exception
- Updated LS client
- Changed name of setting pythonCommand to pythonPath
- Cleanup in the code

## 0.0.2 - 2018-02-17

### Added in 0.0.2

- Added KvLang language server
- Improved syntaxes of KvLang
- Corrected few snippets
- Added basic parser for the KvLang using language server. Parsing errors are displayed during saving file
- Added settings for KvLang extension

## 0.0.1 - 2018-01-20

### Added in 0.0.1

- Initial release
- Added basic syntaxes of KvLang
- Added basic language configuration
- Added kivy language snippets
- Added basic snippets of the uix widget names

## [Unreleased] <https://github.com/Monk3yDev/kvlang-vscode>
