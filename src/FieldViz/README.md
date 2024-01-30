# MockLimelight

The idea of this sub-project is to create a mock Limelight server that can be used for testing purposes. The mock server will be able to respond to the same requests as the real Limelight server, but will not actually do anything. This will allow us to test the client code without having to actually connect to a real Limelight server. The premise is that we can have a GUI that pushes data into the `limelight` network table and perhaps also simultaneously visualize that data, but this would be accessible from the robot python code simultaneously (since this is just hooking up to a Network Table).

The main question I have is whether I have to do this entirely by hand or if we can adopt the Field2D object in the Glass Dashboard.