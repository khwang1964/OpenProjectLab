# Architecture

                     CLI
                      │
                      ▼
              Argument Parser
                      │
                      ▼
                 Registry
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
 Bootstrap     CourseGenerator   WeekGenerator
        │
        ▼
    Template Engine
        │
        ▼
     File System

#
     ProjectConfig
        │
        ▼
Configuration
        │
        ▼
GeneratorContext
        │
        ▼
Generator
