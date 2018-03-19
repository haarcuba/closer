class RemoteProcessException( Exception ):
    pass

class RemoteProcessError( RemoteProcessException ):
    def __init__( self, popenDetails, causedBy ):
        self.popenDetails = popenDetails
        self.exitCode = causedBy.returncode
        self.causedBy = causedBy
        Exception.__init__( self, 'remote process finished with exit code {}: popenDetails={}'.format( self.exitCode, popenDetails ) )

class RemoteProcessTimeout( RemoteProcessException ):
    pass
