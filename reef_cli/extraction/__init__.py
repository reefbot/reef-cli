import pathlib


# pass in a project root directory
# find all python files
# build dependency graph(s)
#    definitions are root nodes.
#    filter out defs and deps that aren't part of project - potentially first extract all defs and then deps (imports)
# extract slices
# provide slice filtering capability (filter design pattern) configurable filters
# prune slices ready for ingestion to LLM


# filtering params extracted using CST
# number of lines
# number of nesting
# number of usages
# usage depth and breadth (how many and how far it's used)
# usage distance (how many directory hops) analogue to coupling
