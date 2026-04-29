import string
from pathlib import Path
from typing import Self

class JobScript():
    """Generic wrapper class for script objects. Treats scripts as strings with
    {variable_names} as place holders for passing arguments at run time Example use cases are
    for running Mechanical ACT Scripts from a remote session or running APDL scripts from
    python and by passing full scripts to the MAPDL instance using /input command.
    """

    def __init__(self,*,path:Path, **args:dict[str,float|int|str|bool]) -> Self:
        self.__path = path
        self.__args = args

    @property
    def path(self) -> Path:
        """Path to the ACT script template"""
        return self.__path
        
    @property
    def template(self) -> str:
        """
        Property that reads the raw script template from the file specified by path
        """
        if self.__path is not None and self.__path.exists():
            with open(self.__path, "r") as file:
                return file.read()
        else:
            raise FileNotFoundError(f"Script file {self.__path} not found.")
        
    @property
    def script(self) -> str:
        """Main property for this class, returns the script with all args passed in via the
        constructor filled in"""
        return (
            self.template
            .replace("{}","{{}}")
            .format(**self.__args)
            )
    
    @property
    def args(self) -> dict[str,float|int|str|bool]:
        """Reveals the args that have been passed in to be used in the script template"""
        return self.__args
    
    @property 
    def expected_args(self) -> list[str]:
        """Reveals the variable names that are expected to be passed in based on the format
        fields found in the script template"""
        return [
            field_name 
            for _, field_name, _, _ in string.Formatter().parse(self.template) 
            if (field_name not in {None, "", " "})
            ]
    
    

def main():
    #Path to script file, note this has been modified to include format string fields for passing values to the script
    path = Path("./cantilever.py")

    "Remember to update your path"
    mat_path = "\"".join(["", str(Path(r".\structural_steel.xml").as_posix()), ""]) 
    #Demonstrate passing args to script 
    dims = {"width":25.0, "height":75.0, "depth":1000.0, "unit": "'mm'", "material": mat_path}

    #NOTE Demnonstrate passing additional args using kwargs and dict unpacking
    #Result of script 1 is identical to script 2
    script1 = JobScript(path = path, **dims)
    script2 = JobScript(path = path, width=25.0, height=75.0, depth=1000.0, unit="mm", material = mat_path)  

    print("SCRIPT INPUTS:",script1.args)
    print("GENERATED SCRIPT:")
    print(script1.script)
if __name__ == "__main__":
    main()