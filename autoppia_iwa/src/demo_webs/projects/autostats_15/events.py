"""Autostats web_15 events. Payload fields match the frontend logEvent(EVENT_TYPES.XXX, data) dataset."""

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


def _data(backend_event: "BackendEvent") -> dict:
    """Inner data payload from frontend (event_data.data)."""
    data = backend_event.data or {}
    return data.get("data") or {}


class ViewSubnetEvent(Event, BaseEventValidator):
    """Fired when user views a subnet detail page."""

    event_name: str = "VIEW_SUBNET"
    subnet_name: str | None = None
    emission: float | None = None
    price: float | None = None
    priceChange1h: float | None = None
    priceChange24h: float | None = None
    priceChange1w: float | None = None
    priceChange1m: float | None = None
    marketCap: float | None = None
    volume24h: float | None = None

    class ValidationCriteria(BaseModel):
        subnet_name: str | CriterionValue | None = None
        emission: float | CriterionValue | None = None
        price: float | CriterionValue | None = None
        marketCap: float | CriterionValue | None = None
        volume24h: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.subnet_name, criteria.subnet_name),
                self._validate_field(self.emission, criteria.emission),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.marketCap, criteria.marketCap),
                self._validate_field(self.volume24h, criteria.volume24h),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewSubnetEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            subnet_name=d.get("subnet_name"),
            emission=d.get("emission"),
            price=d.get("price"),
            priceChange1h=d.get("priceChange1h"),
            priceChange24h=d.get("priceChange24h"),
            priceChange1w=d.get("priceChange1w"),
            priceChange1m=d.get("priceChange1m"),
            marketCap=d.get("marketCap"),
            volume24h=d.get("volume24h"),
        )


class ViewValidatorEvent(Event, BaseEventValidator):
    """Fired when user views a validator detail page."""

    event_name: str = "VIEW_VALIDATOR"
    hotkey: str | None = None
    rank: int | None = None
    dominance: float | None = None
    nominatorCount: int | None = None
    nominatorChange24h: int | None = None
    activeSubnets: int | None = None
    totalWeight: float | None = None
    weightChange24h: float | None = None
    rootStake: float | None = None
    alphaStake: float | None = None
    commission: float | None = None

    class ValidationCriteria(BaseModel):
        hotkey: str | CriterionValue | None = None
        rank: int | CriterionValue | None = None
        dominance: float | CriterionValue | None = None
        nominatorCount: int | CriterionValue | None = None
        totalWeight: float | CriterionValue | None = None
        rootStake: float | CriterionValue | None = None
        alphaStake: float | CriterionValue | None = None
        commission: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.hotkey, criteria.hotkey),
                self._validate_field(self.rank, criteria.rank),
                self._validate_field(self.dominance, criteria.dominance),
                self._validate_field(self.nominatorCount, criteria.nominatorCount),
                self._validate_field(self.totalWeight, criteria.totalWeight),
                self._validate_field(self.rootStake, criteria.rootStake),
                self._validate_field(self.alphaStake, criteria.alphaStake),
                self._validate_field(self.commission, criteria.commission),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewValidatorEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hotkey=d.get("hotkey"),
            rank=d.get("rank"),
            dominance=d.get("dominance"),
            nominatorCount=d.get("nominatorCount"),
            nominatorChange24h=d.get("nominatorChange24h"),
            activeSubnets=d.get("activeSubnets"),
            totalWeight=d.get("totalWeight"),
            weightChange24h=d.get("weightChange24h"),
            rootStake=d.get("rootStake"),
            alphaStake=d.get("alphaStake"),
            commission=d.get("commission"),
        )


class ViewBlockEvent(Event, BaseEventValidator):
    """Fired when user views a block detail page."""

    event_name: str = "VIEW_BLOCK"
    number: int | None = None
    block_timestamp: str | None = None  # block's timestamp (ISO); base Event has timestamp (unix)
    hash: str | None = None
    parentHash: str | None = None
    stateRoot: str | None = None
    extrinsicsRoot: str | None = None
    specVersion: int | None = None
    validator: str | None = None
    timeSinceLastBlock: float | None = None
    epoch: int | None = None
    extrinsicsCount: int | None = None
    eventsCount: int | None = None
    extrinsics: list | None = None

    class ValidationCriteria(BaseModel):
        number: int | CriterionValue | None = None
        hash: str | CriterionValue | None = None
        validator: str | CriterionValue | None = None
        epoch: int | CriterionValue | None = None
        extrinsicsCount: int | CriterionValue | None = None
        eventsCount: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.number, criteria.number),
                self._validate_field(self.hash, criteria.hash),
                self._validate_field(self.validator, criteria.validator),
                self._validate_field(self.epoch, criteria.epoch),
                self._validate_field(self.extrinsicsCount, criteria.extrinsicsCount),
                self._validate_field(self.eventsCount, criteria.eventsCount),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewBlockEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            number=d.get("number"),
            block_timestamp=d.get("timestamp"),
            hash=d.get("hash"),
            parentHash=d.get("parentHash"),
            stateRoot=d.get("stateRoot"),
            extrinsicsRoot=d.get("extrinsicsRoot"),
            specVersion=d.get("specVersion"),
            validator=d.get("validator"),
            timeSinceLastBlock=d.get("timeSinceLastBlock"),
            epoch=d.get("epoch"),
            extrinsicsCount=d.get("extrinsicsCount"),
            eventsCount=d.get("eventsCount"),
            extrinsics=d.get("extrinsics"),
        )


class ViewAccountEvent(Event, BaseEventValidator):
    """Fired when user views an account detail page."""

    event_name: str = "VIEW_ACCOUNT"
    rank: int | None = None
    address: str | None = None
    balance: float | None = None
    stakedAmount: float | None = None
    stakingRatio: float | None = None
    balanceChange24h: float | None = None
    accountType: str | None = None
    lastActive: str | None = None

    class ValidationCriteria(BaseModel):
        rank: int | CriterionValue | None = None
        address: str | CriterionValue | None = None
        balance: float | CriterionValue | None = None
        stakedAmount: float | CriterionValue | None = None
        stakingRatio: float | CriterionValue | None = None
        accountType: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.rank, criteria.rank),
                self._validate_field(self.address, criteria.address),
                self._validate_field(self.balance, criteria.balance),
                self._validate_field(self.stakedAmount, criteria.stakedAmount),
                self._validate_field(self.stakingRatio, criteria.stakingRatio),
                self._validate_field(self.accountType, criteria.accountType),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewAccountEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            rank=d.get("rank"),
            address=d.get("address"),
            balance=d.get("balance"),
            stakedAmount=d.get("stakedAmount"),
            stakingRatio=d.get("stakingRatio"),
            balanceChange24h=d.get("balanceChange24h"),
            accountType=d.get("accountType"),
            lastActive=d.get("lastActive"),
        )


class ExecuteBuyEvent(Event, BaseEventValidator):
    """Fired when user confirms a buy order (market/limit)."""

    event_name: str = "EXECUTE_BUY"
    subnet_name: str | None = None
    orderType: str | None = None
    amountTAU: float | None = None
    amountAlpha: float | None = None
    priceImpact: float | None = None
    maxAvailableTAU: float | None = None

    class ValidationCriteria(BaseModel):
        subnet_name: str | CriterionValue | None = None
        orderType: str | CriterionValue | None = None
        amountTAU: float | CriterionValue | None = None
        amountAlpha: float | CriterionValue | None = None
        priceImpact: float | CriterionValue | None = None
        maxAvailableTAU: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.subnet_name, criteria.subnet_name),
                self._validate_field(self.orderType, criteria.orderType),
                self._validate_field(self.amountTAU, criteria.amountTAU),
                self._validate_field(self.amountAlpha, criteria.amountAlpha),
                self._validate_field(self.priceImpact, criteria.priceImpact),
                self._validate_field(self.maxAvailableTAU, criteria.maxAvailableTAU),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ExecuteBuyEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            subnet_name=d.get("subnet_name"),
            orderType=d.get("orderType"),
            amountTAU=d.get("amountTAU"),
            amountAlpha=d.get("amountAlpha"),
            priceImpact=d.get("priceImpact"),
            maxAvailableTAU=d.get("maxAvailableTAU"),
        )


class ExecuteSellEvent(Event, BaseEventValidator):
    """Fired when user confirms a sell order (market/limit)."""

    event_name: str = "EXECUTE_SELL"
    subnet_name: str | None = None
    orderType: str | None = None
    amountTAU: float | None = None
    amountAlpha: float | None = None
    priceImpact: float | None = None
    maxDelegatedAlpha: float | None = None

    class ValidationCriteria(BaseModel):
        subnet_name: str | CriterionValue | None = None
        orderType: str | CriterionValue | None = None
        amountTAU: float | CriterionValue | None = None
        amountAlpha: float | CriterionValue | None = None
        priceImpact: float | CriterionValue | None = None
        maxDelegatedAlpha: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.subnet_name, criteria.subnet_name),
                self._validate_field(self.orderType, criteria.orderType),
                self._validate_field(self.amountTAU, criteria.amountTAU),
                self._validate_field(self.amountAlpha, criteria.amountAlpha),
                self._validate_field(self.priceImpact, criteria.priceImpact),
                self._validate_field(self.maxDelegatedAlpha, criteria.maxDelegatedAlpha),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ExecuteSellEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            subnet_name=d.get("subnet_name"),
            orderType=d.get("orderType"),
            amountTAU=d.get("amountTAU"),
            amountAlpha=d.get("amountAlpha"),
            priceImpact=d.get("priceImpact"),
            maxDelegatedAlpha=d.get("maxDelegatedAlpha"),
        )


class ConnectWalletEvent(Event, BaseEventValidator):
    """Fired when user connects a wallet (Polkadot.js, Talisman, SubWallet)."""

    event_name: str = "CONNECT_WALLET"
    wallet_name: str | None = None
    address: str | None = None

    class ValidationCriteria(BaseModel):
        wallet_name: str | CriterionValue | None = None
        address: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.wallet_name, criteria.wallet_name),
                self._validate_field(self.address, criteria.address),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ConnectWalletEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            wallet_name=d.get("wallet_name"),
            address=d.get("address"),
        )


class DisconnectWalletEvent(Event, BaseEventValidator):
    """Fired when user disconnects the wallet."""

    event_name: str = "DISCONNECT_WALLET"
    wallet_name: str | None = None
    address: str | None = None

    class ValidationCriteria(BaseModel):
        wallet_name: str | CriterionValue | None = None
        address: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.wallet_name, criteria.wallet_name),
                self._validate_field(self.address, criteria.address),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DisconnectWalletEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            wallet_name=d.get("wallet_name"),
            address=d.get("address"),
        )


class TransferCompleteEvent(Event, BaseEventValidator):
    """Fired when a transfer completes successfully (hash, from, to, amount, block_number)."""

    event_name: str = "TRANSFER_COMPLETE"
    hash: str | None = None
    from_: str | None = None
    to: str | None = None
    amount: float | None = None
    block_number: int | None = None

    class ValidationCriteria(BaseModel):
        hash: str | CriterionValue | None = None
        from_: str | CriterionValue | None = None
        to: str | CriterionValue | None = None
        amount: float | CriterionValue | None = None
        block_number: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.hash, criteria.hash),
                self._validate_field(self.from_, criteria.from_),
                self._validate_field(self.to, criteria.to),
                self._validate_field(self.amount, criteria.amount),
                self._validate_field(self.block_number, criteria.block_number),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "TransferCompleteEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hash=d.get("hash"),
            from_=d.get("from"),
            to=d.get("to"),
            amount=d.get("amount"),
            block_number=d.get("block_number"),
        )


class FavoriteSubnetEvent(Event, BaseEventValidator):
    """Fired when user adds a subnet to favorites (from subnet detail page)."""

    event_name: str = "FAVORITE_SUBNET"
    subnet_id: int | None = None
    subnet_name: str | None = None

    class ValidationCriteria(BaseModel):
        subnet_id: int | CriterionValue | None = None
        subnet_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.subnet_id, criteria.subnet_id),
                self._validate_field(self.subnet_name, criteria.subnet_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FavoriteSubnetEvent":
        base_event = Event.parse(backend_event)
        d = _data(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            subnet_id=d.get("subnet_id"),
            subnet_name=d.get("subnet_name"),
        )


EVENTS = [
    ViewSubnetEvent,
    ViewValidatorEvent,
    ViewBlockEvent,
    ViewAccountEvent,
    ExecuteBuyEvent,
    ExecuteSellEvent,
    ConnectWalletEvent,
    DisconnectWalletEvent,
    TransferCompleteEvent,
    FavoriteSubnetEvent,
]

BACKEND_EVENT_TYPES = {
    "VIEW_SUBNET": ViewSubnetEvent,
    "VIEW_VALIDATOR": ViewValidatorEvent,
    "VIEW_BLOCK": ViewBlockEvent,
    "VIEW_ACCOUNT": ViewAccountEvent,
    "EXECUTE_BUY": ExecuteBuyEvent,
    "EXECUTE_SELL": ExecuteSellEvent,
    "CONNECT_WALLET": ConnectWalletEvent,
    "DISCONNECT_WALLET": DisconnectWalletEvent,
    "TRANSFER_COMPLETE": TransferCompleteEvent,
    "FAVORITE_SUBNET": FavoriteSubnetEvent,
}
