from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class VehicleCost(BaseModel):
    currency: str
    value: float


class VehicleAttribute(BaseModel):
    key: str
    title: str
    value: str
    attributeType: Optional[str] = None
    iconUrl: Optional[str] = None

class UpsellReason(BaseModel):
    title: str
    description: Optional[str] = None

class Vehicle(BaseModel):
    id: str
    brand: str
    model: str
    acrissCode: str
    images: List[str] = []
    bagsCount: int
    passengersCount: int
    groupType: Optional[str] = None
    tyreType: Optional[str] = None
    transmissionType: Optional[str] = None
    fuelType: Optional[str] = None
    isNewCar: Optional[bool] = None
    isRecommended: Optional[bool] = None
    isMoreLuxury: Optional[bool] = None
    isExcitingDiscount: Optional[bool] = None
    attributes: List[VehicleAttribute] = []
    vehicleStatus: Optional[str] = None
    vehicleCost: Optional[VehicleCost] = None
    upsellReasons: List[UpsellReason] = Field(default_factory=list)

class PriceDisplay(BaseModel):
    currency: str
    amount: float
    prefix: Optional[str] = None
    suffix: Optional[str] = None


class VehiclePricing(BaseModel):
    discountPercentage: float
    displayPrice: PriceDisplay
    totalPrice: PriceDisplay


class SelectedVehicle(BaseModel):
    vehicle: Vehicle
    pricing: VehiclePricing
    dealInfo: Optional[str] = None
    tags: List[str] = []


class Booking(BaseModel):
    id: str
    bookedCategory: Optional[str] = None
    protectionPackages: Optional[dict] = None
    createdAt: datetime
    selectedVehicle: Optional[SelectedVehicle] = None
    status: str

class UserPreferences(BaseModel):
    # Minimal for now
    min_seats: Optional[int] = None
    max_daily_price: Optional[float] = None
    wants_automatic: Optional[bool] = None
    extra_luggage: Optional[bool] = None


class VehicleRecommendation(BaseModel):
    selected_vehicle: SelectedVehicle
    score: float
    reason: str

####################### Protection packages #######################

class CurrencyValue(BaseModel):
    currency: str
    value: float


class CoverageItem(BaseModel):
    id: str
    title: str
    description: str
    tags: List[str] = []


class ProtectionPrice(BaseModel):
    discountPercentage: Optional[float] = None
    displayPrice: "PriceDisplay"
    listPrice: Optional["PriceDisplay"] = None
    totalPrice: Optional["PriceDisplay"] = None


class ProtectionPackage(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    deductibleAmount: CurrencyValue
    ratingStars: int
    isPreviouslySelected: bool
    isSelected: bool
    isDeductibleAvailable: bool
    includes: List[CoverageItem] = []
    excludes: List[CoverageItem] = []
    price: ProtectionPrice
    isNudge: bool

###################### Add-Ons ########################

class AddonPrice(BaseModel):
    discountPercentage: Optional[float] = None
    displayPrice: "PriceDisplay"       # riuso ancora PriceDisplay
    totalPrice: Optional["PriceDisplay"] = None  # non sempre presente


class SelectionStrategy(BaseModel):
    isMultiSelectionAllowed: bool
    maxSelectionLimit: int
    currentSelection: int


class AddonChargeDetail(BaseModel):
    id: str
    title: str
    description: str
    iconUrl: Optional[str] = None
    tags: List[str] = []


class AddonAdditionalInfo(BaseModel):
    price: AddonPrice
    isPreviouslySelected: bool
    isSelected: bool
    isEnabled: bool
    selectionStrategy: SelectionStrategy
    isNudge: bool


class AddonOption(BaseModel):
    chargeDetail: AddonChargeDetail
    additionalInfo: AddonAdditionalInfo


class AddonGroup(BaseModel):
    id: int           # l’API ritorna 0, 1, 2... quindi usiamo int
    name: str
    options: List[AddonOption]

###################### Chat Classes ########################

class ChatRequest(BaseModel):
    booking_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str
    booking: Booking
    step: str | None = None

    # Step vehicle
    available_vehicles: List[SelectedVehicle] = []
    recommendations: List[VehicleRecommendation] = []

    # Step protections
    protection_packages: list[ProtectionPackage] | None = None

    # Step addons
    addons: list[AddonGroup] | None = None

