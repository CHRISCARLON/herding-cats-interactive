from HerdingCats.config.sources import (
    CkanDataCatalogues,
    OpenDataSoftDataCatalogues,
    FrenchGouvCatalogue,
)

catalogues = {
    # CKAN Catalogs
    "london-datastore": ("ckan", CkanDataCatalogues.LONDON_DATA_STORE),
    "uk-gov": ("ckan", CkanDataCatalogues.UK_GOV),
    "subak": ("ckan", CkanDataCatalogues.SUBAK),
    "humanitarian-open-data": ("ckan", CkanDataCatalogues.HUMANITARIAN_DATA_STORE),
    "open-africa": ("ckan", CkanDataCatalogues.OPEN_AFRICA),
    # OpenDataSoft Catalogs
    "uk-power-networks": (
        "opendatasoft",
        OpenDataSoftDataCatalogues.UK_POWER_NETWORKS_DNO,
    ),
    "infrabel": ("opendatasoft", OpenDataSoftDataCatalogues.INFRABEL),
    "paris": ("opendatasoft", OpenDataSoftDataCatalogues.PARIS),
    "toulouse": ("opendatasoft", OpenDataSoftDataCatalogues.TOULOUSE),
    "elia-energy": ("opendatasoft", OpenDataSoftDataCatalogues.ELIA_BELGIAN_ENERGY),
    "edf-energy": ("opendatasoft", OpenDataSoftDataCatalogues.EDF_ENERGY),
    "cadent-gas": ("opendatasoft", OpenDataSoftDataCatalogues.CADENT_GAS_GDN),
    "grd-france": ("opendatasoft", OpenDataSoftDataCatalogues.GRD_FRANCE),
    # French Government Catalog
    "french-gov": ("french_gov", FrenchGouvCatalogue.GOUV_FR),
}
