# SPUR

**A codebase navigation and dependency tracing tool for PHP.**

SPUR is an experimental developer tool designed to make navigating large, complicated PHP codebases easier.

The project is motivated by the difficulties of working with legacy PHP applications: large procedural files, extensive dependencies, inconsistent structure and codebases that have evolved over many years. My team at work will regularly be inspecting legacy code made up of hundreds of files, each with dozens of imports and thousands of lines code written before PHP had OOP support.

My goal is to build a tool that can analyse a PHP project, identify its structure and dependencies, and help developers understand how different parts of the application connect.

## Vision

SPUR aims to provide:

- **Codebase indexing:** Identify classes, interfaces, traits, methods and functions across a project.
- **Dependency analysis:** Discover relationships between files, imports and declarations and visualisation of said relationships.
- **Symbol resolution:** Trace where functions, methods and other symbols are defined and referenced.
- **Code navigation:** Follow execution and dependency paths across files.
- **Visualisation:** Present relationships through an interactive, railway-inspired navigation interface.

The central idea is to make unfamiliar and potentially enormous codebases easier to understand without having to manually follow thousands of lines of code.

## Current Development

SPUR is being developed in Python, using Tree-sitter for PHP parsing.

The project is currently in its early stages. Existing work includes PHP syntax parsing, symbol extraction, namespace awareness, qualified names, import extraction and basic file dependency extraction.

Many planned features are still under development.

---

## IMPORTANT: AI USAGE DISCLOSURE

**All tests and test fixtures currently included in this repository were generated using AI.**

The implementation and source code of SPUR, outside of those tests and fixtures, are written by me with assistance from AI tools. AI has been used for programming guidance, explanations, debugging assistance and architectural discussion.

This project is an independent learning and development exercise, and I aim to understand and take responsibility for the code I introduce into the repository. Any code written by AI, I make sure to fully understand what the code does and, where possible, optimise it myself.
