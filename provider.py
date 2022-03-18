import re
import logging
import json
import random
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from config import _config
from scanner import ProductScanner
from queries import Queries
from database import MySQLDatabase
from bricklink import Bricklink
from send_mail import send_mail


class Galaxus(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Galaxus'

    def init_scan(self):
        base_url = 'https://www.galaxus.ch/api/graphql/stellapolaris/brand/product-type-filter-products'
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0',
            'content-type': 'application/json'
        }
        payload = '[{"operationName":"PRODUCT_TYPE_FILTER_PRODUCTS","variables":{"productTypeId":277,"offset":REPLACE_HERE,"limit":60,"sortOrder":"BESTSELLER","siteId":null,"filters":[{"identifier":"bra","filterType":"TEXTUAL","options":["763"]}]},"query":"query PRODUCT_TYPE_FILTER_PRODUCTS($productTypeId: Int\u0021, $filters: [SearchFilter\u0021], $sortOrder: ProductSort, $offset: Int, $siteId: String, $limit: Int) {\\n  productType(id: $productTypeId) {\\n    filterProducts(\\n      offset: $offset\\n      limit: $limit\\n      sort: $sortOrder\\n      siteId: $siteId\\n      filters: $filters\\n    ) {\\n      products {\\n        hasMore\\n        results {\\n          ...ProductWithOffer\\n          __typename\\n        }\\n        __typename\\n      }\\n      counts {\\n        total\\n        filteredTotal\\n        __typename\\n      }\\n      filters {\\n        identifier\\n        name\\n        filterType\\n        score\\n        tooltip {\\n          ...FilterTooltipResult\\n          __typename\\n        }\\n        ...CheckboxSearchFilterResult\\n        ...RangeSearchFilterResult\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment ProductWithOffer on ProductWithOffer {\\n  mandatorSpecificData {\\n    ...ProductMandatorSpecific\\n    __typename\\n  }\\n  product {\\n    ...ProductMandatorIndependent\\n    __typename\\n  }\\n  offer {\\n    ...ProductOffer\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment FilterTooltipResult on FilterTooltip {\\n  text\\n  moreInformationLink\\n  __typename\\n}\\n\\nfragment CheckboxSearchFilterResult on CheckboxSearchFilter {\\n  options {\\n    identifier\\n    name\\n    productCount\\n    score\\n    referenceValue {\\n      value\\n      unit {\\n        abbreviation\\n        __typename\\n      }\\n      __typename\\n    }\\n    preferredValue {\\n      value\\n      unit {\\n        abbreviation\\n        __typename\\n      }\\n      __typename\\n    }\\n    tooltip {\\n      ...FilterTooltipResult\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment RangeSearchFilterResult on RangeSearchFilter {\\n  referenceMin\\n  preferredMin\\n  referenceMax\\n  preferredMax\\n  referenceStepSize\\n  preferredStepSize\\n  rangeMergeInfo {\\n    isBottomMerged\\n    isTopMerged\\n    __typename\\n  }\\n  referenceUnit {\\n    abbreviation\\n    __typename\\n  }\\n  preferredUnit {\\n    abbreviation\\n    __typename\\n  }\\n  rangeFilterDataPoint {\\n    ...RangeFilterDataPointResult\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ProductMandatorSpecific on MandatorSpecificData {\\n  isBestseller\\n  isDeleted\\n  showroomSites\\n  sectorIds\\n  __typename\\n}\\n\\nfragment ProductMandatorIndependent on ProductV2 {\\n  id\\n  productId\\n  name\\n  nameProperties\\n  productTypeId\\n  productTypeName\\n  brandId\\n  brandName\\n  averageRating\\n  totalRatings\\n  totalQuestions\\n  isProductSet\\n  images {\\n    url\\n    height\\n    width\\n    __typename\\n  }\\n  energyEfficiency {\\n    energyEfficiencyColorType\\n    energyEfficiencyLabelText\\n    energyEfficiencyLabelSigns\\n    energyEfficiencyImage {\\n      url\\n      height\\n      width\\n      __typename\\n    }\\n    __typename\\n  }\\n  seo {\\n    seoProductTypeName\\n    seoNameProperties\\n    productGroups {\\n      productGroup1\\n      productGroup2\\n      productGroup3\\n      productGroup4\\n      __typename\\n    }\\n    gtin\\n    __typename\\n  }\\n  hasVariants\\n  smallDimensions\\n  basePrice {\\n    priceFactor\\n    value\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ProductOffer on OfferV2 {\\n  id\\n  productId\\n  offerId\\n  shopOfferId\\n  price {\\n    amountIncl\\n    amountExcl\\n    currency\\n    fraction\\n    __typename\\n  }\\n  deliveryOptions {\\n    mail {\\n      classification\\n      futureReleaseDate\\n      __typename\\n    }\\n    pickup {\\n      siteId\\n      classification\\n      futureReleaseDate\\n      __typename\\n    }\\n    detailsProvider {\\n      productId\\n      offerId\\n      quantity\\n      type\\n      __typename\\n    }\\n    __typename\\n  }\\n  label\\n  type\\n  volumeDiscountPrices {\\n    minAmount\\n    price {\\n      amountIncl\\n      amountExcl\\n      currency\\n      __typename\\n    }\\n    isDefault\\n    __typename\\n  }\\n  salesInformation {\\n    numberOfItems\\n    numberOfItemsSold\\n    isEndingSoon\\n    validFrom\\n    __typename\\n  }\\n  incentiveText\\n  isIncentiveCashback\\n  isNew\\n  isSalesPromotion\\n  hideInProductDiscovery\\n  canAddToBasket\\n  hidePrice\\n  insteadOfPrice {\\n    type\\n    price {\\n      amountIncl\\n      amountExcl\\n      currency\\n      fraction\\n      __typename\\n    }\\n    __typename\\n  }\\n  minOrderQuantity\\n  __typename\\n}\\n\\nfragment RangeFilterDataPointResult on RangeFilterDataPoint {\\n  count\\n  referenceValue {\\n    value\\n    unit {\\n      abbreviation\\n      __typename\\n    }\\n    __typename\\n  }\\n  preferredValue {\\n    value\\n    unit {\\n      abbreviation\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n"}]'
        # payload = '[{"operationName":"GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS","variables":{"productTypeId":277,"queryString":"","offset":REPLACE_HERE,"limit":50,"sort":"BESTSELLER","siteId":null,"sectorId":5,"withDefaultOffer":true},"query":"query GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS($productTypeId: Int!, $queryString: String!, $offset: Int, $limit: Int, $sort: ProductSort, $siteId: String, $sectorId: Int, $withDefaultOffer: Boolean) {\\n  productType(id: $productTypeId) {\\n    filterProductsV4(queryString: $queryString, offset: $offset, limit: $limit, sort: $sort, siteId: $siteId, sectorId: $sectorId, withDefaultOffer: $withDefaultOffer) {\\n      productCounts {\\n        total\\n        filteredTotal\\n        __typename\\n      }\\n      productFilters {\\n        filterGroupType\\n        label\\n        key\\n        tooltip {\\n          ...Tooltip\\n          __typename\\n        }\\n        ...CheckboxFilterGroup\\n        ...RangeSliderFilterGroup\\n        __typename\\n      }\\n      products {\\n        hasMore\\n        results {\\n          ...Product\\n          __typename\\n        }\\n        resultsWithDefaultOffer {\\n          ...ProductWithOffer\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment Tooltip on Tooltip {\\n  text\\n  moreInformationLink\\n  __typename\\n}\\n\\nfragment CheckboxFilterGroup on CheckboxFilterGroupV2 {\\n  filterOptions {\\n    ...Filter\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment RangeSliderFilterGroup on RangeSliderFilterGroupV2 {\\n  dataPoints {\\n    ...RangeSliderDataPoint\\n    __typename\\n  }\\n  selectedRange {\\n    min\\n    max\\n    __typename\\n  }\\n  optionIdentifierKey\\n  unitAbbreviation\\n  unitDisplayOrder\\n  totalCount\\n  fullRange {\\n    min\\n    max\\n    __typename\\n  }\\n  stepSize\\n  mergeInfo {\\n    isBottomMerged\\n    isTopMerged\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Product on Product {\\n  id\\n  productIdAsString\\n  productTypeIdAsString\\n  productTypeName\\n  imageUrl\\n  imageSet {\\n    alternateText\\n    source\\n    __typename\\n  }\\n  sectorId\\n  name\\n  brandId\\n  brandName\\n  fullName\\n  simpleName\\n  nameProperties\\n  productConditionLabel\\n  marketingDescription\\n  pricing {\\n    supplierId\\n    secondHandSalesOfferId\\n    price {\\n      ...VatMoney\\n      __typename\\n    }\\n    priceRebateFraction\\n    insteadOfPrice {\\n      type\\n      price {\\n        ...VatMoneySum\\n        __typename\\n      }\\n      __typename\\n    }\\n    volumeDiscountPrices {\\n      minAmount\\n      price {\\n        ...VatMoneySum\\n        __typename\\n      }\\n      isDefault\\n      __typename\\n    }\\n    __typename\\n  }\\n  availability {\\n    icon\\n    mail {\\n      siteId\\n      title\\n      type\\n      icon\\n      text\\n      description\\n      tooltipDescription\\n      deliveryDate\\n      __typename\\n    }\\n    pickup {\\n      title\\n      notAllowedText\\n      description\\n      isAllowed\\n      __typename\\n    }\\n    pickMup {\\n      description\\n      isAllowed\\n      __typename\\n    }\\n    sites {\\n      siteId\\n      title\\n      type\\n      icon\\n      text\\n      description\\n      tooltipDescription\\n      deliveryDate\\n      __typename\\n    }\\n    isFloorDeliveryAllowed\\n    __typename\\n  }\\n  energyEfficiency {\\n    energyEfficiencyColorType\\n    energyEfficiencyLabelText\\n    energyEfficiencyLabelSigns\\n    energyEfficiencyImageUrl\\n    __typename\\n  }\\n  salesInformation {\\n    numberOfItems\\n    numberOfItemsSold\\n    isLowAmountRemaining\\n    __typename\\n  }\\n  showroomSites\\n  rating\\n  totalRatings\\n  totalQuestions\\n  isIncentiveCashback\\n  incentiveText\\n  isNew\\n  isBestseller\\n  isProductSet\\n  isSalesPromotion\\n  isComparable\\n  isDeleted\\n  isHidden\\n  canAddToBasket\\n  hidePrice\\n  germanNames {\\n    germanProductTypeName\\n    nameWithoutProperties\\n    germanProductNameProperties\\n    germanNameWithBrand\\n    __typename\\n  }\\n  productGroups {\\n    productGroup1\\n    productGroup2\\n    productGroup3\\n    productGroup4\\n    __typename\\n  }\\n  isOtherMandatorProduct\\n  __typename\\n}\\n\\nfragment ProductWithOffer on ProductWithOffer {\\n  mandatorSpecificData {\\n    ...ProductMandatorSpecific\\n    __typename\\n  }\\n  product {\\n    ...ProductMandatorIndependent\\n    __typename\\n  }\\n  offer {\\n    ...ProductOffer\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Filter on Filter {\\n  optionIdentifierKey\\n  optionIdentifierValue\\n  label\\n  productCount\\n  selected\\n  tooltip {\\n    ...Tooltip\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment RangeSliderDataPoint on RangeSliderDataPoint {\\n  value\\n  productCount\\n  __typename\\n}\\n\\nfragment VatMoney on VatMoney {\\n  amountIncl\\n  amountExcl\\n  fraction\\n  currency\\n  __typename\\n}\\n\\nfragment VatMoneySum on VatMoneySum {\\n  amountIncl\\n  amountExcl\\n  currency\\n  __typename\\n}\\n\\nfragment ProductMandatorSpecific on MandatorSpecificData {\\n  isBestseller\\n  isDeleted\\n  showroomSites\\n  sectorIds\\n  __typename\\n}\\n\\nfragment ProductMandatorIndependent on ProductV2 {\\n  id\\n  productId\\n  name\\n  nameProperties\\n  productTypeId\\n  productTypeName\\n  brandId\\n  brandName\\n  averageRating\\n  totalRatings\\n  totalQuestions\\n  isProductSet\\n  images {\\n    url\\n    height\\n    width\\n    __typename\\n  }\\n  energyEfficiency {\\n    energyEfficiencyColorType\\n    energyEfficiencyLabelText\\n    energyEfficiencyLabelSigns\\n    energyEfficiencyImage {\\n      url\\n      height\\n      width\\n      __typename\\n    }\\n    __typename\\n  }\\n  seo {\\n    seoProductTypeName\\n    seoNameProperties\\n    productGroups {\\n      productGroup1\\n      productGroup2\\n      productGroup3\\n      productGroup4\\n      __typename\\n    }\\n    gtin\\n    __typename\\n  }\\n  lowQualityImagePlaceholder\\n  hasVariants\\n  smallDimensions\\n  __typename\\n}\\n\\nfragment ProductOffer on OfferV2 {\\n  id\\n  productId\\n  offerId\\n  shopOfferId\\n  price {\\n    amountIncl\\n    amountExcl\\n    currency\\n    fraction\\n    __typename\\n  }\\n  deliveryOptions {\\n    mail {\\n      classification\\n      futureReleaseDate\\n      __typename\\n    }\\n    pickup {\\n      siteId\\n      classification\\n      futureReleaseDate\\n      __typename\\n    }\\n    detailsProvider {\\n      productId\\n      offerId\\n      quantity\\n      type\\n      __typename\\n    }\\n    certainty\\n    __typename\\n  }\\n  supplier {\\n    name\\n    countryIsoCode\\n    countryName\\n    deliversFromAbroad\\n    __typename\\n  }\\n  label\\n  type\\n  volumeDiscountPrices {\\n    minAmount\\n    price {\\n      amountIncl\\n      amountExcl\\n      currency\\n      __typename\\n    }\\n    isDefault\\n    __typename\\n  }\\n  salesInformation {\\n    numberOfItems\\n    numberOfItemsSold\\n    isEndingSoon\\n    validFrom\\n    __typename\\n  }\\n  incentiveText\\n  isIncentiveCashback\\n  isNew\\n  isSalesPromotion\\n  hideInProductDiscovery\\n  canAddToBasket\\n  hidePrice\\n  insteadOfPrice {\\n    type\\n    price {\\n      amountIncl\\n      amountExcl\\n      currency\\n      fraction\\n      __typename\\n    }\\n    __typename\\n  }\\n  minOrderQuantity\\n  __typename\\n}\\n"}]'
        offset = 0
        has_more = True
        while has_more:
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), base_url))
            try_number = 0
            while try_number <= 11:
                try_number += 1
                logging.info('[{}] Try {}'.format(
                    self.provider.upper(), try_number))
                response = self._get_json(url=base_url, headers=headers, data=payload.replace(
                    'REPLACE_HERE', str(offset)))
                if response[0].get('data'):
                    has_more = response[0]['data']['productType']['filterProducts']['products']['hasMore']
                    tmp_products = response[0]['data']['productType']['filterProducts']['products']['results']
                    offset += 50
                    logging.info('[{}] Found {} products to scan ...'.format(
                        self.provider.upper(), len(tmp_products)))
                    [self.products.append(product) for product in tmp_products]
                    break
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        base_url_product = 'https://www.galaxus.ch/en/product/'
        product_url = "{}{}".format(
            base_url_product, product['product']['productId'])
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        try:
            title = product['product']['name']
            price = product['offer']['price']['amountIncl']
            availability = product['offer']['deliveryOptions']['mail']['classification']
            set_numbers = self._get_set_numbers_from_string(
                product['product']['nameProperties'])
            for set_number in set_numbers:
                self.p.add_product(set_number, title, price, 'CHF',
                                   product_url, availability, self.provider, self.scan_id)
        except:
            logging.warning("[{}] Error parsing: {}".format(
                self.provider.upper(), product_url))


class LEGO(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'LEGOcom'
        self.db = MySQLDatabase()
        self.q = Queries()

    def init_scan(self):
        url = 'https://www.lego.com/api/graphql/ContentPageQuery'
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
            'x-locale': 'de-CH',
            'content-type': 'application/json',
        }
        jsonPayload = '{"operationName":"ContentPageQuery","variables":{"page":PAGE_NUMBER_HERE,"isPaginated":true,"perPage":18,"sort":{"key":"FEATURED","direction":"DESC"},"filters":[],"slug":"REPLACE_HERE","searchSessionId":2},"query":"query ContentPageQuery($slug: String!, $perPage: Int, $page: Int, $isPaginated: Boolean!, $sort: SortInput, $filters: [Filter!]) {\\n  contentPage(slug: $slug) {\\n    id\\n    analyticsGroup\\n    analyticsPageTitle\\n    metaTitle\\n    metaDescription\\n    metaOpenGraph {\\n      title\\n      description\\n      imageUrl\\n      __typename\\n    }\\n    url\\n    title\\n    displayTitleOnPage\\n    ...Breadcrumbs\\n    sections {\\n      ... on LayoutSection {\\n        ...PageLayoutSection\\n        __typename\\n      }\\n      ...ContentSections\\n      ... on TargetedSection {\\n        fetchOnClient\\n        section {\\n          ...ContentSections\\n          ... on LayoutSection {\\n            ...PageLayoutSection\\n            __typename\\n          }\\n          ... on ProductCarouselSection {\\n            ...ProductCarousel_UniqueFields\\n            productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n              ...Product_ProductItem\\n              __typename\\n            }\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on SplitTestingSection {\\n        variantId\\n        testId\\n        optimizelyEntityId\\n        inExperimentAudience\\n        section {\\n          ...ContentSections\\n          ... on LayoutSection {\\n            ...PageLayoutSection\\n            __typename\\n          }\\n          ... on ProductCarouselSection {\\n            ...ProductCarousel_UniqueFields\\n            productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n              ...Product_ProductItem\\n              __typename\\n            }\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on ProductSection {\\n        removePadding\\n        ... on DisruptorProductSection {\\n          ...DisruptorSection\\n          __typename\\n        }\\n        ... on CountdownProductSection {\\n          ...CountdownSection\\n          __typename\\n        }\\n        products(perPage: $perPage, page: $page, sort: $sort, filters: $filters) @include(if: $isPaginated) {\\n          ...ProductListings\\n          __typename\\n        }\\n        products(page: $page, perPage: $perPage, sort: $sort, filters: $filters) @skip(if: $isPaginated) {\\n          ...ProductListings\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on ProductCarouselSection {\\n        ...ProductCarousel_UniqueFields\\n        productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n          ...Product_ProductItem\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment ContentSections on ContentSection {\\n  __typename\\n  id\\n  ...UserGeneratedContentData\\n  ...AccordionSectionData\\n  ...BreadcrumbSection\\n  ...CategoryListingSection\\n  ...ListingBannerSection\\n  ...CardContentSection\\n  ...CopyContent\\n  ...CopySectionData\\n  ...QuickLinksData\\n  ...ContentBlockMixedData\\n  ...HeroBannerData\\n  ...MotionBannerData\\n  ...MotionSidekickData\\n  ...InPageNavData\\n  ...GalleryData\\n  ...TableData\\n  ...RecommendationSectionData\\n  ...SidekickBannerData\\n  ...TextBlockData\\n  ...TextBlockSEOData\\n  ...CountdownBannerData\\n  ...CrowdTwistWidgetSection\\n  ...CodedSection\\n  ...GridSectionData\\n  ...StickyCTAData\\n  ...AudioSectionData\\n  ...MotionSidekick1x1Data\\n}\\n\\nfragment AccordionSectionData on AccordionSection {\\n  __typename\\n  title\\n  showTitle\\n  accordionblocks {\\n    title\\n    text\\n    __typename\\n  }\\n}\\n\\nfragment PageLayoutSection on LayoutSection {\\n  __typename\\n  id\\n  backgroundColor\\n  removePadding\\n  fullWidth\\n  innerSection: section {\\n    id\\n    ...ContentSections\\n    ... on ProductCarouselSection {\\n      ...ProductCarousel_UniqueFields\\n      productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n        ...Product_ProductItem\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment BreadcrumbSection on BreadcrumbSection {\\n  ...BreadcrumbDynamicSection\\n  __typename\\n}\\n\\nfragment BreadcrumbDynamicSection on BreadcrumbSection {\\n  breadcrumbs {\\n    label\\n    url\\n    analyticsTitle\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ListingBannerSection on ListingBannerSection {\\n  ...ListingBanner\\n  __typename\\n}\\n\\nfragment ListingBanner on ListingBannerSection {\\n  title\\n  description\\n  contrast\\n  logoImage\\n  backgroundImages {\\n    small {\\n      ...ImageAsset\\n      __typename\\n    }\\n    medium {\\n      ...ImageAsset\\n      __typename\\n    }\\n    large {\\n      ...ImageAsset\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ImageAsset on ImageAssetDetails {\\n  url\\n  width\\n  height\\n  maxPixelDensity\\n  format\\n  __typename\\n}\\n\\nfragment CategoryListingSection on CategoryListingSection {\\n  ...CategoryListing\\n  __typename\\n}\\n\\nfragment CategoryListing on CategoryListingSection {\\n  title\\n  description\\n  thumbnailImage\\n  children {\\n    ...CategoryLeafSection\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CategoryLeafSection on CategoryListingChildren {\\n  title\\n  description\\n  thumbnailImage\\n  logoImage\\n  url\\n  ageRange\\n  tag\\n  thumbnailSrc {\\n    ...ImageAsset\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment DisruptorSection on DisruptorProductSection {\\n  disruptor {\\n    ...DisruptorData\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment DisruptorData on Disruptor {\\n  __typename\\n  imageSrc {\\n    ...ImageAsset\\n    __typename\\n  }\\n  contrast\\n  background\\n  title\\n  description\\n  link\\n  openInNewTab\\n}\\n\\nfragment ProductListings on ProductQueryResult {\\n  count\\n  offset\\n  total\\n  optimizelyExperiment {\\n    testId\\n    variantId\\n    __typename\\n  }\\n  results {\\n    ...Product_ProductItem\\n    __typename\\n  }\\n  facets {\\n    ...Facet_FacetSidebar\\n    __typename\\n  }\\n  sortOptions {\\n    ...Sort_SortOptions\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Product_ProductItem on Product {\\n  __typename\\n  id\\n  productCode\\n  name\\n  slug\\n  primaryImage(size: THUMBNAIL)\\n  baseImgUrl: primaryImage\\n  overrideUrl\\n  ... on ReadOnlyProduct {\\n    readOnlyVariant {\\n      ...Variant_ReadOnlyProduct\\n      __typename\\n    }\\n    __typename\\n  }\\n  ... on SingleVariantProduct {\\n    variant {\\n      ...Variant_ListingProduct\\n      __typename\\n    }\\n    __typename\\n  }\\n  ... on MultiVariantProduct {\\n    priceRange {\\n      formattedPriceRange\\n      formattedListPriceRange\\n      __typename\\n    }\\n    variants {\\n      ...Variant_ListingProduct\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment Variant_ListingProduct on ProductVariant {\\n  id\\n  sku\\n  salePercentage\\n  attributes {\\n    rating\\n    maxOrderQuantity\\n    availabilityStatus\\n    availabilityText\\n    vipAvailabilityStatus\\n    vipAvailabilityText\\n    canAddToBag\\n    canAddToWishlist\\n    vipCanAddToBag\\n    onSale\\n    isNew\\n    ...ProductAttributes_Flags\\n    __typename\\n  }\\n  ...ProductVariant_Pricing\\n  __typename\\n}\\n\\nfragment ProductVariant_Pricing on ProductVariant {\\n  price {\\n    formattedAmount\\n    centAmount\\n    currencyCode\\n    formattedValue\\n    __typename\\n  }\\n  listPrice {\\n    formattedAmount\\n    centAmount\\n    __typename\\n  }\\n  attributes {\\n    onSale\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ProductAttributes_Flags on ProductAttributes {\\n  featuredFlags {\\n    key\\n    label\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Variant_ReadOnlyProduct on ReadOnlyVariant {\\n  id\\n  sku\\n  attributes {\\n    featuredFlags {\\n      key\\n      label\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Facet_FacetSidebar on Facet {\\n  name\\n  key\\n  id\\n  labels {\\n    __typename\\n    displayMode\\n    name\\n    labelKey\\n    count\\n    ... on FacetValue {\\n      value\\n      __typename\\n    }\\n    ... on FacetRange {\\n      from\\n      to\\n      __typename\\n    }\\n  }\\n  __typename\\n}\\n\\nfragment Sort_SortOptions on SortOptions {\\n  id\\n  key\\n  direction\\n  label\\n  __typename\\n}\\n\\nfragment CardContentSection on CardContentSection {\\n  ...CardContent\\n  __typename\\n}\\n\\nfragment CardContent on CardContentSection {\\n  moduleTitle\\n  showModuleTitle\\n  blocks {\\n    title\\n    isH1\\n    description\\n    textAlignment\\n    primaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    logoPosition\\n    imageSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    callToActionText\\n    callToActionLink\\n    altText\\n    contrast\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CopyContent on CopyContentSection {\\n  blocks {\\n    title\\n    body\\n    textAlignment\\n    titleColor\\n    imageSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CopySectionData on CopySection {\\n  title\\n  showTitle\\n  body\\n  __typename\\n}\\n\\nfragment QuickLinksData on QuickLinkSection {\\n  title\\n  quickLinks {\\n    title\\n    isH1\\n    link\\n    openInNewTab\\n    contrast\\n    imageSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ContentBlockMixedData on ContentBlockMixed {\\n  moduleTitle\\n  showModuleTitle\\n  blocks {\\n    title\\n    isH1\\n    description\\n    backgroundColor\\n    blockTheme\\n    contentPosition\\n    logoURL\\n    logoPosition\\n    callToActionText\\n    callToActionLink\\n    altText\\n    backgroundImages {\\n      largeImage {\\n        small {\\n          ...ImageAsset\\n          __typename\\n        }\\n        large {\\n          ...ImageAsset\\n          __typename\\n        }\\n        __typename\\n      }\\n      smallImage {\\n        small {\\n          ...ImageAsset\\n          __typename\\n        }\\n        large {\\n          ...ImageAsset\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment UserGeneratedContentData on UserGeneratedContent {\\n  ugcBlock {\\n    title\\n    text\\n    ugcType\\n    ugcKey\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment HeroBannerData on HeroBanner {\\n  heroblocks {\\n    id\\n    title\\n    isH1\\n    tagline\\n    bannerTheme\\n    contentVerticalPosition\\n    contentHorizontalPosition\\n    contentHeight\\n    primaryLogoSrcNew {\\n      ...ImageAsset\\n      __typename\\n    }\\n    secondaryLogoSrcNew {\\n      ...ImageAsset\\n      __typename\\n    }\\n    videoMedia {\\n      url\\n      id\\n      isLiveStream\\n      __typename\\n    }\\n    logoPosition\\n    contentBackground\\n    callToActionText\\n    callToActionLink\\n    secondaryCallToActionText\\n    secondaryCallToActionLink\\n    secondaryOpenInNewTab\\n    backgroundImagesNew {\\n      small {\\n        ...ImageAsset\\n        __typename\\n      }\\n      medium {\\n        ...ImageAsset\\n        __typename\\n      }\\n      large {\\n        ...ImageAsset\\n        __typename\\n      }\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment GalleryData on Gallery {\\n  galleryblocks {\\n    id\\n    contentHeight\\n    primaryLogoSrcNew {\\n      ...ImageAsset\\n      __typename\\n    }\\n    videoMedia {\\n      url\\n      id\\n      isLiveStream\\n      __typename\\n    }\\n    backgroundImagesNew {\\n      small {\\n        ...ImageAsset\\n        __typename\\n      }\\n      medium {\\n        ...ImageAsset\\n        __typename\\n      }\\n      large {\\n        ...ImageAsset\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment MotionBannerData on MotionBanner {\\n  motionBannerBlocks {\\n    id\\n    title\\n    isH1\\n    tagline\\n    bannerTheme\\n    contentHorizontalPosition\\n    primaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    animatedMedia\\n    videoMedia {\\n      url\\n      id\\n      isLiveStream\\n      __typename\\n    }\\n    logoPosition\\n    contentBackground\\n    callToActionText\\n    callToActionLink\\n    backgroundImages {\\n      small {\\n        ...ImageAsset\\n        __typename\\n      }\\n      medium {\\n        ...ImageAsset\\n        __typename\\n      }\\n      large {\\n        ...ImageAsset\\n        __typename\\n      }\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment MotionSidekickData on MotionSidekick {\\n  motionSidekickBlocks {\\n    id\\n    title\\n    isH1\\n    tagline\\n    bannerTheme\\n    contentHorizontalPosition\\n    primaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    animatedMedia\\n    videoMedia {\\n      url\\n      id\\n      isLiveStream\\n      __typename\\n    }\\n    logoPosition\\n    contentBackground\\n    callToActionText\\n    callToActionLink\\n    backgroundImages {\\n      small {\\n        ...ImageAsset\\n        __typename\\n      }\\n      medium {\\n        ...ImageAsset\\n        __typename\\n      }\\n      large {\\n        ...ImageAsset\\n        __typename\\n      }\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment InPageNavData on InPageNav {\\n  inPageNavBlocks {\\n    id\\n    title\\n    isH1\\n    text\\n    contrast\\n    primaryLogoSrc\\n    secondaryLogoSrc\\n    animatedMedia\\n    videoMedia {\\n      url\\n      id\\n      __typename\\n    }\\n    contentBackground\\n    backgroundImages {\\n      small\\n      medium\\n      large\\n      __typename\\n    }\\n    callToActionText\\n    callToActionLink\\n    openInNewTab\\n    secondaryCallToActionText\\n    secondaryCallToActionLink\\n    secondaryOpenInNewTab\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment TableData on TableSection {\\n  rows {\\n    isHeadingRow\\n    cells\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment RecommendationSectionData on RecommendationSection {\\n  __typename\\n  title\\n  showTitle\\n  recommendationType\\n}\\n\\nfragment SidekickBannerData on SidekickBanner {\\n  __typename\\n  id\\n  sidekickBlocks {\\n    title\\n    isH1\\n    text\\n    textAlignment\\n    contrast\\n    backgroundColor\\n    logoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    logoPosition\\n    ctaTextPrimary: ctaText\\n    ctaLinkPrimary: ctaLink\\n    ctaTextSecondary\\n    ctaLinkSecondary\\n    contentHeight\\n    bgImages {\\n      large\\n      __typename\\n    }\\n    videoMedia {\\n      url\\n      id\\n      isLiveStream\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n}\\n\\nfragment ProductCarousel_UniqueFields on ProductCarouselSection {\\n  __typename\\n  productCarouselTitle: title\\n  showTitle\\n  showAddToBag\\n  seeAllLink\\n}\\n\\nfragment TextBlockData on TextBlock {\\n  textBlocks {\\n    title\\n    isH1\\n    text\\n    textAlignment\\n    contrast\\n    backgroundColor\\n    callToActionLink\\n    callToActionText\\n    openInNewTab\\n    secondaryCallToActionLink\\n    secondaryCallToActionText\\n    secondaryOpenInNewTab\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment TextBlockSEOData on TextBlockSEO {\\n  textBlocks {\\n    title\\n    text\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Countdown on CountdownBannerChild {\\n  title\\n  isH1\\n  text\\n  textPosition\\n  textAlignment\\n  contrast\\n  backgroundColor\\n  callToActionLink\\n  callToActionText\\n  openInNewTab\\n  countdownDate\\n  __typename\\n}\\n\\nfragment CountdownBannerData on CountdownBanner {\\n  countdownBannerBlocks {\\n    ...Countdown\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CountdownSection on CountdownProductSection {\\n  countdown {\\n    ...Countdown\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CrowdTwistWidgetSection on CrowdTwistWidgetSection {\\n  __typename\\n  id\\n  heading\\n  activityId\\n  rewardId\\n}\\n\\nfragment CodedSection on CodedSection {\\n  __typename\\n  id\\n  componentName\\n  properties {\\n    key\\n    value\\n    __typename\\n  }\\n  text {\\n    key\\n    value\\n    __typename\\n  }\\n  media {\\n    key\\n    values {\\n      id\\n      contentType\\n      fileSize\\n      filename\\n      url\\n      title\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment GridSectionData on GridSection {\\n  items {\\n    id\\n    image\\n    videoMedia {\\n      id\\n      url\\n      isLiveStream\\n      __typename\\n    }\\n    href\\n    text\\n    textContrast\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment AudioSectionData on AudioSection {\\n  tracks {\\n    trackArt {\\n      ...ImageAsset\\n      __typename\\n    }\\n    src\\n    title\\n    description\\n    __typename\\n  }\\n  backgroundColor\\n  textContrast\\n  backgroundImage {\\n    mobile {\\n      ...ImageAsset\\n      __typename\\n    }\\n    desktop {\\n      ...ImageAsset\\n      __typename\\n    }\\n    __typename\\n  }\\n  seriesTitle\\n  seriesThumbnail {\\n    ...ImageAsset\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Breadcrumbs on Content {\\n  breadcrumbs {\\n    __typename\\n    label\\n    url\\n    analyticsTitle\\n  }\\n  __typename\\n}\\n\\nfragment StickyCTAData on StickyCTASection {\\n  item {\\n    backgroundColor\\n    ctaBackgroundImage\\n    ctaPosition\\n    href\\n    text\\n    textAlign\\n    textContrast\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment MotionSidekick1x1Data on MotionSidekick1x1 {\\n  motionSidekickBlocks {\\n    id\\n    title\\n    description\\n    textContrast\\n    contentHorizontalPosition\\n    primaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      ...ImageAsset\\n      __typename\\n    }\\n    inlineVideo {\\n      id\\n      url\\n      isLiveStream\\n      __typename\\n    }\\n    fullVideo {\\n      id\\n      url\\n      isLiveStream\\n      __typename\\n    }\\n    logoHorizontalPosition\\n    backgroundColor\\n    primaryCallToActionText\\n    primaryCallToActionLink\\n    secondaryCallToActionText\\n    secondaryCallToActionLink\\n    __typename\\n  }\\n  __typename\\n}\\n"}'
        for base_url in ['/themes', '/categories/interests']:
            request = self._get_json(url=url, data=jsonPayload.replace(
                'REPLACE_HERE', base_url).replace('PAGE_NUMBER_HERE', '1'), headers=headers)
            themes = request['data']['contentPage']['sections'][0]['children']
            for theme in themes:
                logging.warning('[{}] Parsing theme {} ...'.format(
                    self.provider.upper(), theme['title']))
                tmp_products = []
                has_more = True
                page = 0
                while has_more:
                    page = page+1
                    theme_url = theme['url'].replace('/about', '/products').replace('/campaigns', '/themes').replace(
                        '/supermario', '/super-mario').replace('https://www.lego.com', '')
                    logging.info("[{}] Requesting {} ...".format(
                        self.provider.upper(), theme_url))
                    theme_request = self._get_json(url=url, data=jsonPayload.replace(
                        'REPLACE_HERE', theme_url).replace('PAGE_NUMBER_HERE', str(page)), headers=headers)
                    if theme_request['data']['contentPage']:
                        try:
                            sections = [section for section in theme_request['data']['contentPage']['sections']
                                        if section['__typename'] == 'BasicProductSection' or section['__typename'] == 'DisruptorProductSection']
                            for section in sections:
                                tmp_products += section['products']['results']
                                if section['products']['count'] == 0:
                                    has_more = False
                            else:
                                break
                        except Exception as e:
                            logging.warning('[{}] Couldnt parse theme {} ...'.format(
                                self.provider.upper(), theme_url))
                            print(e)
                logging.info('[{}] Found {} products to scan ...'.format(
                    self.provider.upper(), len(tmp_products)))
                [self.products.append(
                    product) for product in tmp_products if product not in self.products]
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
            self.db.close()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        set_number = product['productCode']
        title = product['name']
        product_url = '{}{}'.format(
            'https://www.lego.com/de-ch/', product['slug'])
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        variantBase = product['variant'] if product.get(
            'variant') else product['variants'][0]
        print(set_number)
        # isEOL = False
        # if variantBase['attributes']['featuredFlags']:
        #     if variantBase['attributes']['featuredFlags'][0]['key'] == 'hardToFind':
        #         isEOL = True
        price = variantBase['price']['centAmount']/100
        currency = variantBase['price']['currencyCode']
        list_price = variantBase['listPrice']['centAmount']/100
        self._update_list_price(set_number, list_price)
        availability = variantBase['attributes']['availabilityStatus']
        self.p.add_product(set_number, title, price, currency,
                           product_url, availability, self.provider, self.scan_id)

    def _update_list_price(self, set_number, list_price):
        to_update = self.q._select_query(
            "SELECT id FROM tbl_sets WHERE set_number = %s AND ch_price IS NULL", (set_number, ))
        ids = [s['id'] for s in to_update]
        if ids:
            for set_id in ids:
                update_data = {
                    'table_name': 'tbl_sets',
                    'data': {
                        'ch_price': list_price
                    },
                    'condition': {
                        'id': set_id
                    }
                }
                logging.info('[{}] Updating list price ({}) for set number {} ...'.format(
                    self.provider.upper(), list_price, set_number))
                self.db._update_query(update_data)


class Smyth(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Smyth'

    def init_scan(self):
        base_url = 'https://www.smythstoys.com/ch/de-ch/ch/de-ch/spielzeug/lego/c/SM100114/load-more?q=%3AbestsellerRating%3AproductVisible%3Atrue&page={}'
        has_more = True
        page = 0
        while has_more:
            url = base_url.format(page)
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), url))
            options = Options()
            options.headless = True
            driver = webdriver.Firefox(options=options)
            driver.add_cookie(
                {'name': 'JSESSIONID', 'value': 'FD5C852B79350551EE01EEB74D540F9C'})
            driver.add_cookie({'name': 'visid_incap_2483049',
                              'value': 'mW8m6k5LTL2rQSP5UpktZvZNG2IAAAAAQUIPAAAAAAAkVOy7qYllS5hqN10Tc/fN'})
            driver.add_cookie({'name': 'incap_ses_448_2483049',
                              'value': 'j0L0DNr2vk8N9AsLM543BgZOG2IAAAAAyDfpf6MlBr4DMrvU9MV2tA=='})
            driver.add_cookie({'name': 'reese84=3:nK4KBkmeJwTBSaNJSX90iA==:o4ImUpZVjtFyY7MRjQdJ9qe7va2ZaT3xHB6az+RW4qyt1HgFOKniHQwxjPMogvxwbS314F3jISD5wGsFE+utLivcNUqzJK8ojnaFlVDQlvHMK+tQe/tXfONcg2+cNaGd03BTL0RfIbQ41WHPycUO0FewShDbvEk/rKvExQJWrDerhhV9gJEqajHaifOX8Idwvn6nSnhFunnYkPxytljqaXZXZj/kNfIiYlCGCsTL8yevwZEC9LaS5hX5846dWyNPZk5kaBsrh3paYGCl/qZjFhfHG3izDuW4qtvuvqZq9eTwi9VoLL87F65TT+eGVvA+6+1QoKwKv36mmfkwDGFTxJTUbsJqyc8awFpBDMdplW0BHIWOMXztxrbn5/0ui9pkTjxv9qpczUxJs4s313DL22ndqG1JR7EaH6DW0soigCCwBp3NZYzB8Kujm0QiQyk26wTuiyXvWw7hXugAsDY7tbOzCHy2qXxXuVZei8iTXcQ=:B1QGNSC5UFa3U1JU0NcD8Ac88MMlDwxyAk7g85RWJ5o='})
            driver.add_cookie({'name': 'uid', 'value': 'ch'})
            driver.add_cookie({'name': 'GCILB', 'value': '"ae33959a2edc0152"'})
            driver.add_cookie(
                {'name': 'nlbi_2483049', 'value': '0P4jGfqyhm9M+INbYsb6kQAAAAAR/kO/c7f+Clp/xhPOSno8'})
            driver.add_cookie(
                {'name': 'smyths_gtm_CYBERSOURCE', 'value': 'false'})
            driver.add_cookie({'name': 'smyths_gtm_KLARNA', 'value': 'false'})
            driver.add_cookie({'name': 'smyths_gtm_GTM', 'value': 'false'})
            driver.add_cookie({'name': 'smyths_gtm_RAKUTEN', 'value': 'false'})
            driver.add_cookie(
                {'name': 'smyths_gtm_BAZAARVOICE', 'value': 'false'})
            driver.add_cookie(
                {'name': 'smyths_gtm_FLIXMEDIA', 'value': 'false'})
            driver.add_cookie(
                {'name': 'smyths_gtm_WEBCOLLAGE', 'value': 'false'})
            driver.add_cookie(
                {'name': 'smyths_gtm_FRESHCHAT', 'value': 'false'})
            driver.add_cookie({'name': 'smyths_gtm_YOUTUBE', 'value': 'false'})
            driver.add_cookie(
                {'name': 'smyths_gtm_LOCATION', 'value': 'false'})
            driver.add_cookie({'name': 'ch-anonymous-consents', 'value': '%5B%7B%22templateCode%22%3A%22Funktionale+Cookies%22%2C%22templateVersion%22%3A0%2C%22consentState%22%3A%22GIVEN%22%7D%2C%7B%22templateCode%22%3A%22Analytische+Cookies%22%2C%22templateVersion%22%3A0%2C%22consentState%22%3A%22GIVEN%22%7D%2C%7B%22templateCode%22%3A%22Werbe-+oder+Targeting+Cookies%22%2C%22templateVersion%22%3A0%2C%22consentState%22%3A%22GIVEN%22%7D%2C%7B%22templateCode%22%3A%22Notwendige+Cookies%22%2C%22templateVersion%22%3A0%2C%22consentState%22%3A%22GIVEN%22%7D%5D'})
            driver.add_cookie(
                {'name': 'smyths_gtm_GOOGLEOPTIMIZE', 'value': 'true'})
            driver.add_cookie({'name': 'smyths_gtm_HOTJAR', 'value': 'true'})
            driver.add_cookie({'name': 'smyths_gtm_GA', 'value': 'true'})
            driver.add_cookie(
                {'name': 'smyths_gtm_GOOGLEADWORDS', 'value': 'true'})
            driver.add_cookie({'name': 'smyths_gtm_FACEBOOK', 'value': 'true'})
            driver.add_cookie({'name': 'nlbi_2483049_2147483392',
                              'value': '7c9XZLu0ElBEuGZhYsb6kQAAAACViHY5WVKOqhrhRziZ0Ptc'})
            driver.add_cookie({'name': '_hjOptOut', 'value': 'false'})
            driver.add_cookie({'name': 'locationCookie', 'value': '_'})
            driver.add_cookie({'name': 'GaPermission', 'value': 'true'})
            driver.get(url)
            print(driver.page_source)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            has_more = soup['hasMoreResults']
            html_soup = BeautifulSoup(soup['htmlContent'], "html.parser")
            tmp_products = html_soup.find_all(
                'div', {'class': 'panel product-panel st-p-relative item-panel'}) if soup else []
            logging.info('[{}] Found {} products to scan ...'.format(
                self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
            page = page + 1
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        href = product.find('a', {'class': 'trackProduct'})['href']
        product_url = '{}{}'.format('https://www.smythstoys.com', href)
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        title = product.find('h2', {'class': 'prodName trackProduct'}).text
        set_numbers = self._get_set_numbers_from_string(title)
        price = product.find('div', {'class': 'price'})['content']
        for set_number in set_numbers:
            if float(price) > 0:
                self.p.add_product(set_number, title, price, 'CHF',
                                   product_url, None, self.provider, self.scan_id)


class Manor(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Manor'

    def init_scan(self):
        base_url = 'https://www.manor.ch/de/shop/spielwaren/lego/c/lego-shop'
        soup = self._get_soup(base_url, self.headers)
        total_pages = int(soup.find('ul', {'class': 'pagination'}).find(
            'li', text=re.compile(r'[0-9]')).text)
        logging.info("[{}] Found a total pages of {} ...".format(
            self.provider.upper(), total_pages))
        product_url = 'https://www.manor.ch/Shop/Spielwaren/LEGO/c/lego-shop/getarticleforpage?q=&page={}&sort=top-seller&bv=false'
        for page in range(0, total_pages):
            url = product_url.format(page)
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), url))
            p_soup = self._get_soup(url, self.headers)
            logging.info(p_soup)
            tmp_products = p_soup.find_all(
                'div', {'class': 'o-producttile'}) if p_soup else []
            logging.info('[{}] Found {} products to scan ...'.format(
                self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        href = product.find('a', {'class': 'o-producttile__link'})['href']
        product_url = '{}{}'.format('https://www.manor.ch', href)
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        title = product.find('div', {
                             'class': 'o-producttile__copy m-productdetailareaa__areaA__title-line-secondline'}).text.strip()
        set_numbers = self._get_set_numbers_from_string(title)
        price = product.find('span', {'class': 'js-productprice'}).text.strip()
        for set_number in set_numbers:
            if float(price) > 0:
                self.p.add_product(set_number, title, price, 'CHF',
                                   product_url, None, self.provider, self.scan_id)


class Velis(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Velis'

    def init_scan(self):
        base_url = 'https://www.velis-spielwaren.ch/de/LEGO%C2%AE+Shop/?first={}'
        index = 0
        tmp_products = True
        while tmp_products:
            url = base_url.format(index)
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), url))
            p_soup = self._get_soup(url, self.headers)
            logging.info(p_soup)
            tmp_products = p_soup.find_all(
                'div', {'class': 'artlistitem'}) if p_soup else []
            logging.info('[{}] Found {} products to scan ...'.format(
                self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
            index += 50
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        href = product.find('div', {'class': 'artlistimg'}).find('a')['href']
        product_url = '{}{}'.format(
            'https://www.velis-spielwaren.ch/de/LEGO%C2%AE+Shop/', href)
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        title = product.find('div', {'class': 'artlistinfo'}).find('a').text
        set_numbers = self._get_set_numbers_from_string(title)
        price = product.find('div', {'class': 'artlistpreis'})
        try:
            price.span.decompose()
            price = self._format_price(price.text)
            availability = product.find(
                'div', {'class': 'artlistlager'}).text.strip()
            for set_number in set_numbers:
                self.p.add_product(set_number, title, price, 'CHF',
                                   product_url, availability, self.provider, self.scan_id)
        except:
            pass


class Alternate(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Alternate'

    def init_scan(self):
        base_url = 'https://www.alternate.ch/listing_ajax.xhtml?t=16680&af=true&listing=1&filter_7171=1557&page={}'
        index = 1
        while True:
            url = base_url.format(index)
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), url))
            options = Options()
            options.headless = True
            options.binary_location = '/home/sergej/bin/firefox/firefox'
            options.executable_path = '/home/sergej/bin/geckodriver'
            driver = webdriver.Firefox(options=options)
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()
            logging.info(soup)
            tmp_products = soup.find_all(
                'a', {'class': 'card text-black productBox boxCounter'}) if soup else []
            if not tmp_products:
                break
            logging.info('[{}] Found {} products to scan ...'.format(
                self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
            index += 1
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        product_url = product['href']
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        title = product.find(
            'div', {'class': 'product-name font-weight-bold'}).text
        price_tag = product.find('span', {'class': 'price'}).text
        price = self._format_price(price_tag.replace('.', ''))
        try:
            availability = product.find(
                'div', {'class': 'col-auto delivery-info text-right'}).find('span').text
            availability = re.sub(r' [0-9]+', '', availability)
        except:
            availability = ''
        set_numbers = self._get_set_numbers_from_string(title)
        if 'Lenovo' not in title:
            for set_number in set_numbers:
                self.p.add_product(set_number, title, price, 'CHF',
                                   product_url, availability, self.provider, self.scan_id)


class Techmania(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Techmania'

    def init_scan(self):
        base_url = 'https://www.techmania.ch/de/Product/list/lego-13278?p={}'
        tmp_products = True
        pageIndex = 1
        while tmp_products:
            url = base_url.format(pageIndex)
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), url))
            soup = self._get_soup(url, self.headers)
            tmp_products = soup.find_all('div', {
                                         'class': 'c12 sm-flex-item md-flex-item lg-flex-item sm12 md6 lg4 xl3 singleItem productGridElement product-element'}) if soup else []
            tmp_product_urls = [item.find('a', {'class': 'itemBox'})[
                'href'] for item in tmp_products]
            logging.info('[{}] Found {} products to scan ...'.format(
                self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_product_urls]
            pageIndex += 1
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product_url):
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        soup = self._get_soup(product_url, self.headers)
        logging.info(soup)
        price = soup.find('p', {'class': 'preisItem'}).find_all('span')[1].text
        price = float(''.join(re.findall('[0-9.]', price)))
        title = soup.find(
            'div', {'class': 'head-product lg7 lg-float-r'}).find('h1').text
        try:
            set_numbers = self._get_set_numbers_from_string(soup.find('div', {'class': 'inner-col-info product-info-desk'}).find(
                'div', {'class': 'product-metadata'}).find('div', {'class': 'product-metadata'}).find_all('span')[1].text)
            for set_number in set_numbers:
                self.p.add_product(set_number, title, price, 'CHF',
                                   product_url, None, self.provider, self.scan_id)
        except:
            pass


class MeinSpielzeug(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'MeinSpielzeug'

    def init_scan(self):
        base_url = 'https://www.meinspielzeug.ch/marke/lego/sortiment/{}'
        soup = self._get_soup(base_url.format(1), self.headers)
        total_pages = soup.find('div', {'class': 'pageturner'}).find_all(
            'li')[-1].find('a').text
        for page in range(1, int(total_pages)+1):
            url = base_url.format(page)
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), url))
            soup = self._get_soup(url, self.headers)
            tmp_products = soup.find_all(
                'div', {'class': 'box-wrapper'}) if soup else []
            logging.info('[{}] Found {} products to scan ...'.format(
                self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        href = product.find('a')['href']
        product_url = '{}{}'.format('https://www.meinspielzeug.ch', href)
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        title = product.find('h3').text
        article_id = product.find('div', {'class': 'button'})['data-artikelid']
        price = self._get_price(article_id)
        set_numbers = self._get_set_numbers_from_string(title)
        for set_number in set_numbers:
            self.p.add_product(set_number, title, price, 'CHF',
                               product_url, None, self.provider, self.scan_id)

    def _get_price(self, article_id):
        article_id = 'AN{}'.format(article_id)
        article_url = 'https://aws.meinspielzeug.ch/lagerbestand/{}'.format(
            article_id)
        try:
            json = requests.get(url=article_url, headers=self.headers).json()
            price = json[0]['wert'].split('|')[3]
            return price
        except:
            return


class Migros(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Migros'

    def init_scan(self):
        base_url = 'https://www.melectronics.ch/jsapi/v1/de/products/search/category/2723017907?viewAll=&pageSize=200&currentPage={}'
        json = requests.get(url=base_url.format(
            0), headers=self.headers).json()
        total_pages = json['pagination']['totalPages']
        for page in range(0, total_pages):
            url = base_url.format(page)
            logging.info("[{}] Requesting {} ...".format(
                self.provider.upper(), url))
            r_json = self._get_json(
                url=url, headers=self.headers, request_type='get')
            tmp_products = r_json['products'] if r_json else []
            logging.info('[{}] Found {} products to scan ...'.format(
                self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
        logging.info('[{}] Found a total of {} products ...'.format(
            self.provider.upper(), len(self.products)))
        if len(self.products) > 0:
            [self._scan_product(product)
             for product in self.products[:_config['scanner']['limit']]]
            self.p.deploy_to_database()
        else:
            body = "Seht us als waer dr Scanner fuer {} dunde ...".format(
                self.provider)
            subject = '[L-PVG] {}|Scanning Error ...'.format(self.provider)
            to = _config['notification']['email']
            send_mail(to, subject, body)

    def _scan_product(self, product):
        product_url = '{}{}'.format(
            'https://www.melectronics.ch', product['url'])
        logging.info("[{}] Scanning product {} ...".format(
            self.provider.upper(), product_url))
        title = product['name']
        set_numbers = self._get_set_numbers_from_string(title)
        if product.get('price'):
            price = product['price']['value']
            availability = 'AVAILABLE' if product['orderable'] else 'UNAVAILABLE'
            for set_number in set_numbers:
                self.p.add_product(set_number, title, price, 'CHF',
                                   product_url, availability, self.provider, self.scan_id)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.DEBUG)
    p = LEGO()
    p.init_scan()
