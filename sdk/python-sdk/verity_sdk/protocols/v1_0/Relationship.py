from enum import Enum

from verity_sdk.protocols.Protocol import Protocol
from verity_sdk.utils import EVERNYM_MSG_QUALIFIER



class GoalsList(Enum):
    """An enumeration of possible goals (reasons) for a relationship."""
    class GoalCode:
        """
        a tuple with a short code string and human readable name string
        """
        def __init__(self, code, name) -> None:
            """
            Args:
                code (str): short code string
                name (str): human readable string
            """
            self.code = code
            self.name = name

    ISSUE_VC = GoalCode('issue-vc', 'To issue a credential')
    """To issue a credential"""

    REQUEST_PROOF = GoalCode('request-proof', 'To request a proof')
    """To request a proof"""

    CREATE_ACCOUNT = GoalCode('create-account', 'To create an account with a service')
    """To create an account with a service"""

    P2P_MESSAGING = GoalCode('p2p-messaging', 'To establish a peer-to-peer messaging relationship')
    """To establish a peer-to-peer messaging relationship"""


class Relationship(Protocol):
    """
    The Relationship protocol creates and manages relationships on the verity-application agent. These relationships
    are secure communication channels between self-sovereign parties. A relationship much be created before using the
    connections protocols. In the future this protocol will allow management of each given relationship
    (eg key rotation)
    """
    MSG_FAMILY = 'relationship'
    """the family name for the message family"""

    MSG_FAMILY_VERSION = '1.0'
    """the version for the message family"""

    CREATED = 'created'
    """Name for 'created' signal message"""
    INVITATION = 'invitation'
    """Name for 'invitation' signal message"""

    CREATE = 'create'
    """Name for 'create' control message"""
    CONNECTION_INVITATION = 'connection-invitation'
    """Name for 'connection-invitation' control message"""
    OUT_OF_BAND_INVITATION = 'out-of-band-invitation'
    """Name for 'out-of-band-invitation' control message"""

    def __init__(self,
                 for_relationship: str = None,
                 thread_id: str = None,
                 label: str = None,
                 logo_url: str = None):
        """
        Args:
            for_relationship (str): the relationship identifier (DID) for the pairwise relationship that will be used
            thread_id (str): the thread id of the already started protocol
            label (str): he label presented in the invitation to connect to this relationship
            logo_url (str): logo url presented in invitation
        """
        super().__init__(
            self.MSG_FAMILY,
            self.MSG_FAMILY_VERSION,
            msg_qualifier=EVERNYM_MSG_QUALIFIER,
            thread_id=thread_id
        )

        self.for_relationship = for_relationship
        if label:
            self.label = label
        else:
            self.label = ''
        self.goal = GoalsList.P2P_MESSAGING
        self.logo_url = logo_url

    async def create(self, context):
        """
        Directs verity-application to create a new relationship

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent
        """
        await self.send_message(context, await self.create_msg_packed(context))

    def create_msg(self, _):
        """
        Creates the control message without packaging and sending it.

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent

        Return:
            the constructed message (dict object)
        """
        msg = self._get_base_message(self.CREATE)
        self._add_thread(msg)
        msg['label'] = self.label
        if self.logo_url:
            msg['logoUrl'] = self.logo_url

        return msg

    async def create_msg_packed(self, context):
        """
        Creates and packages message without sending it.

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent

        Return:
            the bytes ready for transport
        """
        return await self.get_message_bytes(context, self.create_msg(context))

    async def connection_invitation(self, context):
        """
        Ask for aries invitation from the verity-application agent for the relationship created by this protocol

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent
        """
        await self.send_message(context, await self.connection_invitation_msg_packed(context))

    def connection_invitation_msg(self, _):
        """
        Creates the control message without packaging and sending it.

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent

        Return:
            the constructed message (dict object)
        """
        msg = self._get_base_message(self.CONNECTION_INVITATION)
        self._add_thread(msg)
        self._add_relationship(msg, self.for_relationship)
        return msg

    async def connection_invitation_msg_packed(self, context):
        """
        Creates and packages message without sending it.

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent

        Return:
            the bytes ready for transport
        """
        return await self.get_message_bytes(context, self.connection_invitation_msg(context))

    async def out_of_band_invitation(self, context):
        """
        Ask for aries out of band invitation from the verity-application agent for the relationship created by this protocol

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent
        """
        await self.send_message(context, await self.out_of_band_invitation_msg_packed(context))

    def out_of_band_invitation_msg(self, _):
        """
        Creates the control message without packaging and sending it.

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent

        Return:
            the constructed message (dict object)
        """
        msg = self._get_base_message(self.OUT_OF_BAND_INVITATION)
        msg['goalCode'] = self.goal.value.code
        msg['goal'] = self.goal.value.name
        self._add_thread(msg)
        self._add_relationship(msg, self.for_relationship)
        return msg

    async def out_of_band_invitation_msg_packed(self, context):
        """
        Creates and packages message without sending it.

        Args:
            context (Context): an instance of the Context object initialized to a verity-application agent

        Return:
            the bytes ready for transport
        """
        return await self.get_message_bytes(context, self.out_of_band_invitation_msg(context))
