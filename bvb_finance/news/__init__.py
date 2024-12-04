import typing
from bvb_finance import logging

logger = logging.getLogger()

class UIActiveComponent:
    components_metadata = dict()

    class ActiveComponent:
        def __init__(self, index):
            self.index = index

    @classmethod
    def register_components(cls, name: str, components_number: int):
        logger.info("UIActiveComponent.register_components: " +
                    f"Registering {components_number} components for name {name}")
        cls.components_metadata[name] = [None] * components_number
    
    @classmethod
    def update_components(cls, name, new_values: typing.List) -> ActiveComponent:
        if name not in cls.components_metadata:
            logger.error(f"Name {name} is not registered with UIActiveComponent")
            return
        old_values = cls.components_metadata[name]
        if len(old_values) != len(new_values):
            logger.error(f"UIActiveComponent.update_components(name={name}): " +
                         f"old_values {old_values} mismatch in length new_values {new_values}")
            return
        active_component = None
        for index in range(len(old_values)):
            if old_values[index] != new_values[index]:
                active_component = UIActiveComponent.ActiveComponent(index)
                break

        cls.components_metadata[name] = new_values
        return active_component
