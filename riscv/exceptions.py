class RISCVException(Exception): pass
    
class InvalidInstruction(RISCVException): pass

class MisalignedMemoryAccess(RISCVException): pass

class InvalidMemoryAccess(RISCVException): pass

class DivideByZeroException(RISCVException): pass

class ProgramTerminated(RISCVException): pass

class AssemblerError(RISCVException): pass