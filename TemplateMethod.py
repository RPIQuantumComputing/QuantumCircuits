# Template Method Code Example

# In certain algorithms, there are identical steps that are implementing
# only slightly differently. And, some of the steps are universal, so,
# as the lazy and smart programmers we are, we try to minimize our
# efforts and the chance of making bugs...

# What if we wanted to make a computer?
class Computer:
    # Here are the known steps that are universal
    def addCase(self): pass
    def addPowerSupply(self): pass
    def addMotherboard(self): pass
    def addCPU(self): pass
    def addGPU(self): pass
    def addStorage(self): pass
    # Some are always the same, so let us just implement them here
    def connectCords(self):
        print("Cords connected!")
    # We can also overload methods, so we can make the common behavior the default
    # and override whenver necessary 
    def installOperatingSystem(self):
        print("Windows Installed!")
    def testComputer(self):
        print("Computer Works!")

    # We can pull it all together and make a computer by calling these programs
    def build(self):
        self.addCase()
        self.addPowerSupply()
        self.addMotherboard()
        self.addCPU()
        self.addGPU()
        self.addStorage()
        self.connectCords()
        self.installOperatingSystem()
        self.testComputer()

# Supercomputers take up space and use all the resources
class SuperComputer(Computer):
    def addCase(self):
        print("Building a warehouse...")
        print("Case for Supercomputer Built")
    def addPowerSupply(self):
        print("Placing necessary wiring...")
        print("Power Supply for Supercomputer Installed")
    def addMotherboard(self):
        print("Adding motherboards...")
        print("Motherboards installed")
    def addCPU(self):
        print("Adding CPUs...")
        print("CPUs installed")
    def addGPU(self):
        print("Adding GPUs...")
        print("GPUs installed")
    def addStorage(self):
        print("Adding SSDs...")
        print("Adding Hard Drives...")
        print("Storage Installed")
    def installOperatingSystem(self):
        print("Linux Installed!")

# Gaming computers are just fast regular desktop computers
class GamingComputer(Computer):
    def addCase(self):
        print("Case for Gaming Computer Built")
    def addPowerSupply(self):
        print("Placing necessary wiring...")
        print("Power Supply for Gaming Computer Installed")
    def addMotherboard(self):
        print("Adding motherboard...")
        print("Motherboard installed")
    def addCPU(self):
        print("Adding CPU...")
        print("CPU installed")
    def addGPU(self):
        print("Adding GPU...")
        print("GPU installed")
    def addStorage(self):
        print("Adding SSD...")
        print("Adding Hard Drives for the games...")
        print("Storage Installed")

# Make a supercomputer
supercomputer = SuperComputer()
supercomputer.build()

print("-" * 40)

# Make a gaming computer
gamingcomputer = GamingComputer()
gamingcomputer.build()