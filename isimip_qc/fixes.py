from dataclasses import dataclass


@dataclass
class Fix:
    def __call__(self, file):
        return self.fix(file)

    def fix(self, file):
        raise NotImplementedError


@dataclass
class RenameDimension(Fix):
    dimension_name: str
    new_dimension_name: str

    def fix(self, file):
        file.info('Renaming dimension "%s" -> "%s".', self.dimension_name, self.new_dimension_name)
        if self.dimension_name in file.dataset.dimensions:
            file.dataset.renameDimension(self.dimension_name, self.new_dimension_name)
        else:
            file.error('Cannot apply fix: dimension "%s" not found.', self.dimension_name)


@dataclass
class RenameVariable(Fix):
    variable_name: str
    new_variable_name: str

    def fix(self, file):
        file.info('Renaming variable "%s" -> "%s".', self.variable_name, self.new_variable_name)
        if self.variable_name in file.dataset.variables:
            file.dataset.renameVariable(self.variable_name, self.new_variable_name)
        else:
            file.error('Cannot apply fix: variable "%s" not found.', self.variable_name)


@dataclass
class SetVariableAttr(Fix):
    variable_name: str
    attr_name: str
    value: object

    def fix(self, file):
        file.info('Setting attribute "%s.%s=%s"', self.variable_name, self.attr_name, self.value)
        if self.variable_name in file.dataset.variables:
            file.dataset.variables[self.variable_name].setncattr(self.attr_name, self.value)
        else:
            file.error('Cannot apply fix: variable "%s" not found.', self.variable_name)


@dataclass
class RenameVariableAttr(Fix):
    variable_name: str
    attr_name: str
    new_attr_name: str

    def fix(self, file):
        file.info(
            'Renaming attribute "%s.%s" -> "%s.%s".',
            self.variable_name,
            self.attr_name,
            self.variable_name,
            self.new_attr_name,
        )
        if self.variable_name in file.dataset.variables:
            file.dataset.variables[self.variable_name].renameAttribute(self.attr_name, self.new_attr_name)
        else:
            file.error('Cannot apply fix: variable "%s" not found.', self.variable_name)


@dataclass
class RemoveVariableAttr(Fix):
    variable_name: str
    attr_name: str

    def fix(self, file):
        file.info('Removing attribute "%s.%s"', self.variable_name, self.attr_name)
        if self.variable_name in file.dataset.variables:
            file.dataset.variables[self.variable_name].delncattr(self.attr_name)
        else:
            file.error('Cannot apply fix: variable "%s" not found.', self.variable_name)


@dataclass
class SetGlobalAttr(Fix):
    attr_name: str
    value: object

    def fix(self, file):
        file.info('Setting global attribute "%s=%s"', self.attr_name, self.value)
        file.dataset.setncattr(self.attr_name, self.value)


@dataclass
class RenameGlobalAttr(Fix):
    attr_name: str
    new_attr_name: str

    def fix(self, file):
        file.info('Renaming global attribute "%s" -> "%s".', self.attr_name, self.new_attr_name)
        if self.attr_name in file.dataset.ncattrs():
            file.dataset.renameAttribute(self.attr_name, self.new_attr_name)
        else:
            file.error('Cannot apply fix: global attribute "%s" not found.', self.attr_name)


@dataclass
class RemoveGlobalAttr(Fix):
    attr_name: str

    def fix(self, file):
        file.info('Removing global attribute "%s"', self.attr_name)
        if self.attr_name in file.dataset.ncattrs():
            file.dataset.delncattr(self.attr_name)
        else:
            file.error('Cannot apply fix: global attribute "%s" not found.', self.attr_name)
