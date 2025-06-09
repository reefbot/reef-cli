from reef_cli.dependencies.dependency import DependencyNode


def get_linked_dependencies(
    candidate, imports
) -> list[DependencyNode]:

    dependencies = []
    for imp in imports:

        # special treatment for * imports
        # match the base of qualified name
        if imp.qualified_name[-1] == "*":
            if ".".join(imp.qualified_name.split(".")[-1]) == ".".join(candidate.qualified_name.split(".")[-1]):
                dependencies.append(imp)

        if imp.qualified_name == candidate.qualified_name:
            dependencies.append(imp)

    return dependencies
