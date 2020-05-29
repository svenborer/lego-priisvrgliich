import re
import logging
import random
import requests

from config import _config
from scanner import ProductScanner
from queries import Queries
from database import MySQLDatabase
from bricklink import Bricklink

class Galaxus(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Galaxus'
    
    def init_scan(self):
        base_url = 'https://www.galaxus.ch/api/graphql'
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'content-type': 'application/json'
        }
        payload = '''
            [
                {
                    "operationName":"GET_PRODUCT_TYPE_PRODUCTS_AND_FILTERS",
                    "variables":{
                        "productTypeId":277,
                        "queryString":"",
                        "offset":REPLACE_HERE,
                        "limit":50,
                        "sort":"BESTSELLER",
                        "siteId":null,
                        "sectorId":5
                    },
                    "extensions":{
                        "persistedQuery":{
                            "version":1,"sha256Hash":"cd2107b20ecd5954254487b28679b7a12d0a42139e5ea1a244fcb281539a6a48"
                        }
                    }
                }
            ]
        '''
        offset = 0
        has_more = True
        while has_more:
            logging.info("[{}] Requesting {} ...".format(self.provider.upper(), base_url))
            json = self._get_json(url=base_url, headers=headers, data=payload.replace('REPLACE_HERE', str(offset)))
            has_more = json[0]['data']['productType']['filterProductsV4']['products']['hasMore']
            tmp_products = json[0]['data']['productType']['filterProductsV4']['products']['results']
            offset += 50
            logging.info('[{}] Found {} products to scan ...'.format(self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
        logging.info('[{}] Found a total of {} products ...'.format(self.provider.upper(), len(self.products)))
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()

    def _scan_product(self, product):
        base_url_product = 'https://www.galaxus.ch/en/product/'
        print(product)
        product_url = "{}{}".format(base_url_product, product['productIdAsString'])
        logging.info("[{}] Scanning product {} ...".format(self.provider.upper(), product_url))
        title = product['name']
        price = product['pricing']['price']['amountIncl']
        availability = product['availability']['mail']['icon']
        set_numbers = self._get_set_numbers_from_string(title)
        for set_number in set_numbers:
            self.p.add_product(set_number, title, price, 'CHF', product_url, availability, self.provider, self.scan_id)

class LEGO(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'LEGOcom'
        self.db = MySQLDatabase()
        self.q = Queries()
    
    def init_scan(self):
        url = 'https://www.lego.com/api/graphql/ContentPageQuery'
        headers = {
            'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36', 
            'x-locale' : 'de-CH', 
            'content-type' : 'application/json'
        }
        jsonPayload = '''
            {
                "operationName":"ContentPageQuery",
                "variables":{
                    "page":1,
                    "isPaginated":false,
                    "perPage":100,
                    "sort":{
                        "key":"FEATURED",
                        "direction":"DESC"
                    },
                    "filters":[],
                    "slug":"REPLACE_HERE",
                    "hideTargetedSections":false
                },
                "query":"query ContentPageQuery($slug: String\u0021, $perPage: Int, $page: Int, $isPaginated: Boolean\u0021, $sort: SortInput, $filters: [Filter\u0021], $hideTargetedSections: Boolean\u0021) {\\n  contentPage(slug: $slug) {\\n    analyticsGroup\\n    analyticsPageTitle\\n    metaTitle\\n    metaDescription\\n    metaOpenGraph {\\n      title\\n      description\\n      imageUrl\\n      __typename\\n    }\\n    url\\n    title\\n    displayTitleOnPage\\n    ...Breadcrumbs\\n    sections {\\n      ... on LayoutSection {\\n        ...PageLayoutSection\\n        __typename\\n      }\\n      ...ContentSections\\n      ... on TargetedSection {\\n        hidden(hideTargetedSections: $hideTargetedSections)\\n        section {\\n          ...ContentSections\\n          ... on LayoutSection {\\n            ...PageLayoutSection\\n            __typename\\n          }\\n          ... on ProductCarouselSection {\\n            ...ProductCarousel_UniqueFields\\n            productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n              ...Product_ProductItem\\n              __typename\\n            }\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on SplitTestingSection {\\n        variantId\\n        testId\\n        optimizelyEntityId\\n        inExperimentAudience\\n        hidden(hideTargetedSections: $hideTargetedSections)\\n        section {\\n          ...ContentSections\\n          ... on LayoutSection {\\n            ...PageLayoutSection\\n            __typename\\n          }\\n          ... on ProductCarouselSection {\\n            ...ProductCarousel_UniqueFields\\n            productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n              ...Product_ProductItem\\n              __typename\\n            }\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on ProductSection {\\n        removePadding\\n        ... on DisruptorProductSection {\\n          ...DisruptorSection\\n          __typename\\n        }\\n        ... on CountdownProductSection {\\n          ...CountdownSection\\n          __typename\\n        }\\n        products(perPage: $perPage, page: $page, sort: $sort, filters: $filters) @include(if: $isPaginated) {\\n          ...ProductListings\\n          __typename\\n        }\\n        products(page: $page, perPage: $perPage, sort: $sort, filters: $filters) @skip(if: $isPaginated) {\\n          ...ProductListings\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on ProductCarouselSection {\\n        ...ProductCarousel_UniqueFields\\n        productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n          ...Product_ProductItem\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment ContentSections on ContentSection {\\n  __typename\\n  id\\n  ...AccordionSectionData\\n  ...BreadcrumbSection\\n  ...CategoryIndexSection\\n  ...CategoryListingSection\\n  ...ListingBannerSection\\n  ...CardContentSection\\n  ...CopyContent\\n  ...CopySectionData\\n  ...QuickLinksData\\n  ...ContentBlockMixedData\\n  ...HeroBannerData\\n  ...MotionBannerData\\n  ...MotionSidekickData\\n  ...InPageNavData\\n  ...GalleryData\\n  ...TableData\\n  ...RecommendationSectionData\\n  ...SidekickBannerData\\n  ...TextBlockData\\n  ...TextBlockSEOData\\n  ...CountdownBannerData\\n  ...CrowdTwistWidgetSection\\n  ...CodedSection\\n}\\n\\nfragment AccordionSectionData on AccordionSection {\\n  __typename\\n  title\\n  showTitle\\n  accordionblocks {\\n    title\\n    text\\n    __typename\\n  }\\n}\\n\\nfragment PageLayoutSection on LayoutSection {\\n  __typename\\n  id\\n  backgroundColor\\n  removePadding\\n  fullWidth\\n  innerSection: section {\\n    ...ContentSections\\n    ... on ProductCarouselSection {\\n      ...ProductCarousel_UniqueFields\\n      productCarouselProducts: products(page: 1, perPage: 16, sort: $sort) {\\n        ...Product_ProductItem\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment CategoryIndexSection on CategoryIndexSection {\\n  ...CategoryIndex\\n  __typename\\n}\\n\\nfragment CategoryIndex on CategoryIndexSection {\\n  title\\n  children {\\n    ...CategoryBannerSection\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CategoryBannerSection on CategoryIndexChildren {\\n  title\\n  description\\n  thumbnailImage\\n  url\\n  thumbnailSrc {\\n    url\\n    width\\n    height\\n    maxPixelDensity\\n    format\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment BreadcrumbSection on BreadcrumbSection {\\n  ...BreadcrumbDynamicSection\\n  __typename\\n}\\n\\nfragment BreadcrumbDynamicSection on BreadcrumbSection {\\n  breadcrumbs {\\n    label\\n    url\\n    analyticsTitle\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ListingBannerSection on ListingBannerSection {\\n  ...ListingBanner\\n  __typename\\n}\\n\\nfragment ListingBanner on ListingBannerSection {\\n  title\\n  description\\n  contrast\\n  logoImage\\n  images {\\n    size\\n    url\\n    __typename\\n  }\\n  backgroundImages {\\n    small {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    medium {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    large {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CategoryListingSection on CategoryListingSection {\\n  ...CategoryListing\\n  __typename\\n}\\n\\nfragment CategoryListing on CategoryListingSection {\\n  title\\n  description\\n  thumbnailImage\\n  children {\\n    ...CategoryLeafSection\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CategoryLeafSection on CategoryListingChildren {\\n  title\\n  description\\n  thumbnailImage\\n  logoImage\\n  url\\n  ageRange\\n  tag\\n  thumbnailSrc {\\n    url\\n    width\\n    height\\n    maxPixelDensity\\n    format\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment DisruptorSection on DisruptorProductSection {\\n  disruptor {\\n    ...DisruptorData\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment DisruptorData on Disruptor {\\n  __typename\\n  image\\n  contrast\\n  background\\n  title\\n  description\\n  link\\n  openInNewTab\\n}\\n\\nfragment ProductListings on ProductQueryResult {\\n  count\\n  offset\\n  total\\n  optimizelyExperiment {\\n    testId\\n    variantId\\n    __typename\\n  }\\n  results {\\n    ...Product_ProductItem\\n    __typename\\n  }\\n  facets {\\n    ...Facet_FacetSidebar\\n    __typename\\n  }\\n  sortOptions {\\n    ...Sort_SortOptions\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Product_ProductItem on Product {\\n  __typename\\n  id\\n  productCode\\n  name\\n  slug\\n  primaryImage(size: THUMBNAIL)\\n  baseImgUrl: primaryImage\\n  overrideUrl\\n  ... on ReadOnlyProduct {\\n    readOnlyVariant {\\n      ...Variant_ReadOnlyProduct\\n      __typename\\n    }\\n    __typename\\n  }\\n  ... on SingleVariantProduct {\\n    variant {\\n      ...Variant_ListingProduct\\n      __typename\\n    }\\n    __typename\\n  }\\n  ... on MultiVariantProduct {\\n    variants {\\n      ...Variant_ListingProduct\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment Variant_ListingProduct on ProductVariant {\\n  id\\n  sku\\n  salePercentage\\n  attributes {\\n    rating\\n    maxOrderQuantity\\n    availabilityStatus\\n    availabilityText\\n    vipAvailabilityStatus\\n    vipAvailabilityText\\n    canAddToBag\\n    canAddToWishlist\\n    vipCanAddToBag\\n    onSale\\n    isNew\\n    ...ProductAttributes_Flags\\n    __typename\\n  }\\n  ...ProductVariant_Pricing\\n  __typename\\n}\\n\\nfragment ProductVariant_Pricing on ProductVariant {\\n  price {\\n    formattedAmount\\n    centAmount\\n    currencyCode\\n    formattedValue\\n    __typename\\n  }\\n  listPrice {\\n    formattedAmount\\n    centAmount\\n    __typename\\n  }\\n  attributes {\\n    onSale\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ProductAttributes_Flags on ProductAttributes {\\n  featuredFlags {\\n    key\\n    label\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Variant_ReadOnlyProduct on ReadOnlyVariant {\\n  id\\n  sku\\n  attributes {\\n    featuredFlags {\\n      key\\n      label\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Facet_FacetSidebar on Facet {\\n  name\\n  key\\n  id\\n  labels {\\n    __typename\\n    displayMode\\n    name\\n    labelKey\\n    count\\n    ... on FacetValue {\\n      value\\n      __typename\\n    }\\n    ... on FacetRange {\\n      from\\n      to\\n      __typename\\n    }\\n  }\\n  __typename\\n}\\n\\nfragment Sort_SortOptions on SortOptions {\\n  id\\n  key\\n  direction\\n  label\\n  __typename\\n}\\n\\nfragment CardContentSection on CardContentSection {\\n  ...CardContent\\n  __typename\\n}\\n\\nfragment CardContent on CardContentSection {\\n  moduleTitle\\n  showModuleTitle\\n  blocks {\\n    title\\n    isH1\\n    description\\n    textAlignment\\n    logo\\n    secondaryLogo\\n    primaryLogoSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    logoPosition\\n    image\\n    imageSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    callToActionText\\n    callToActionLink\\n    altText\\n    contrast\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CopyContent on CopyContentSection {\\n  blocks {\\n    title\\n    body\\n    textAlignment\\n    titleColor\\n    imageSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CopySectionData on CopySection {\\n  title\\n  showTitle\\n  body\\n  __typename\\n}\\n\\nfragment QuickLinksData on QuickLinkSection {\\n  title\\n  quickLinks {\\n    title\\n    isH1\\n    image\\n    link\\n    openInNewTab\\n    contrast\\n    imageSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ContentBlockMixedData on ContentBlockMixed {\\n  moduleTitle\\n  showModuleTitle\\n  blocks {\\n    title\\n    isH1\\n    description\\n    backgroundColor\\n    blockTheme\\n    contentPosition\\n    logoURL\\n    logoPosition\\n    callToActionText\\n    callToActionLink\\n    altText\\n    backgroundImages {\\n      largeImage {\\n        small {\\n          url\\n          width\\n          height\\n          maxPixelDensity\\n          format\\n          __typename\\n        }\\n        large {\\n          url\\n          width\\n          height\\n          maxPixelDensity\\n          format\\n          __typename\\n        }\\n        __typename\\n      }\\n      smallImage {\\n        small {\\n          url\\n          width\\n          height\\n          maxPixelDensity\\n          format\\n          __typename\\n        }\\n        large {\\n          url\\n          width\\n          height\\n          maxPixelDensity\\n          format\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment HeroBannerData on HeroBanner {\\n  heroblocks {\\n    id\\n    title\\n    isH1\\n    tagline\\n    bannerTheme\\n    contentVerticalPosition\\n    contentHorizontalPosition\\n    contentHeight\\n    primaryLogoSrc\\n    primaryLogoSrcNew {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    secondaryLogoSrc\\n    secondaryLogoSrcNew {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    videoMedia {\\n      url\\n      id\\n      __typename\\n    }\\n    logoPosition\\n    contentBackground\\n    callToActionText\\n    callToActionLink\\n    secondaryCallToActionText\\n    secondaryCallToActionLink\\n    secondaryOpenInNewTab\\n    backgroundImagesNew {\\n      small {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      medium {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      large {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      __typename\\n    }\\n    backgroundImages {\\n      small\\n      medium\\n      large\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment GalleryData on Gallery {\\n  galleryblocks {\\n    id\\n    contentHeight\\n    primaryLogoSrc\\n    primaryLogoSrcNew {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    videoMedia {\\n      url\\n      id\\n      __typename\\n    }\\n    backgroundImagesNew {\\n      small {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      medium {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      large {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      __typename\\n    }\\n    backgroundImages {\\n      small\\n      medium\\n      large\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment MotionBannerData on MotionBanner {\\n  motionBannerBlocks {\\n    id\\n    title\\n    isH1\\n    tagline\\n    bannerTheme\\n    contentHorizontalPosition\\n    primaryLogoSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    animatedMedia\\n    videoMedia {\\n      url\\n      id\\n      __typename\\n    }\\n    logoPosition\\n    contentBackground\\n    callToActionText\\n    callToActionLink\\n    backgroundImages {\\n      small {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      medium {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      large {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment MotionSidekickData on MotionSidekick {\\n  motionSidekickBlocks {\\n    id\\n    title\\n    isH1\\n    tagline\\n    bannerTheme\\n    contentHorizontalPosition\\n    primaryLogoSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    secondaryLogoSrc {\\n      url\\n      width\\n      height\\n      maxPixelDensity\\n      format\\n      __typename\\n    }\\n    animatedMedia\\n    videoMedia {\\n      url\\n      id\\n      __typename\\n    }\\n    logoPosition\\n    contentBackground\\n    callToActionText\\n    callToActionLink\\n    backgroundImages {\\n      small {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      medium {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      large {\\n        url\\n        width\\n        height\\n        maxPixelDensity\\n        format\\n        __typename\\n      }\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment InPageNavData on InPageNav {\\n  inPageNavBlocks {\\n    id\\n    title\\n    isH1\\n    text\\n    contrast\\n    textPosition\\n    textAlignment\\n    primaryLogoSrc\\n    secondaryLogoSrc\\n    animatedMedia\\n    videoMedia {\\n      url\\n      id\\n      __typename\\n    }\\n    logoPosition\\n    contentBackground\\n    backgroundImages {\\n      small\\n      medium\\n      large\\n      __typename\\n    }\\n    callToActionText\\n    callToActionLink\\n    openInNewTab\\n    secondaryCallToActionText\\n    secondaryCallToActionLink\\n    secondaryOpenInNewTab\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment TableData on TableSection {\\n  rows {\\n    isHeadingRow\\n    cells\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment RecommendationSectionData on RecommendationSection {\\n  __typename\\n  title\\n  showTitle\\n  recommendationType\\n}\\n\\nfragment SidekickBannerData on SidekickBanner {\\n  __typename\\n  id\\n  sidekickBlocks {\\n    title\\n    isH1\\n    text\\n    textAlignment\\n    contrast\\n    backgroundColor\\n    logo\\n    secondaryLogo\\n    logoPosition\\n    ctaTextPrimary: ctaText\\n    ctaLinkPrimary: ctaLink\\n    ctaTextSecondary\\n    ctaLinkSecondary\\n    contentHeight\\n    bgImages {\\n      large\\n      __typename\\n    }\\n    videoMedia {\\n      url\\n      id\\n      __typename\\n    }\\n    altText\\n    __typename\\n  }\\n}\\n\\nfragment ProductCarousel_UniqueFields on ProductCarouselSection {\\n  __typename\\n  productCarouselTitle: title\\n  showTitle\\n  showAddToBag\\n  seeAllLink\\n}\\n\\nfragment TextBlockData on TextBlock {\\n  textBlocks {\\n    title\\n    isH1\\n    text\\n    textAlignment\\n    contrast\\n    backgroundColor\\n    callToActionLink\\n    callToActionText\\n    openInNewTab\\n    secondaryCallToActionLink\\n    secondaryCallToActionText\\n    secondaryOpenInNewTab\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment TextBlockSEOData on TextBlockSEO {\\n  textBlocks {\\n    title\\n    text\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Countdown on CountdownBannerChild {\\n  title\\n  isH1\\n  text\\n  textPosition\\n  textAlignment\\n  contrast\\n  backgroundColor\\n  callToActionLink\\n  callToActionText\\n  openInNewTab\\n  countdownDate\\n  __typename\\n}\\n\\nfragment CountdownBannerData on CountdownBanner {\\n  countdownBannerBlocks {\\n    ...Countdown\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CountdownSection on CountdownProductSection {\\n  countdown {\\n    ...Countdown\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CrowdTwistWidgetSection on CrowdTwistWidgetSection {\\n  __typename\\n  id\\n  heading\\n  activityId\\n  rewardId\\n}\\n\\nfragment CodedSection on CodedSection {\\n  __typename\\n  id\\n  componentName\\n}\\n\\nfragment Breadcrumbs on Content {\\n  breadcrumbs {\\n    __typename\\n    label\\n    url\\n    analyticsTitle\\n  }\\n  __typename\\n}\\n"
            }
        '''
        request = self._get_json(url=url, data=jsonPayload.replace('REPLACE_HERE', '/themes'), headers=headers)
        themes = request['data']['contentPage']['sections'][1]['children']
        for theme in themes:
            theme_url = theme['url'].replace('/about', '/products')
            logging.info("[{}] Requesting {} ...".format(self.provider.upper(), theme_url))
            theme_request = self._get_json(url=url, data=jsonPayload.replace('REPLACE_HERE', theme_url), headers=headers)
            try:
                tmp_products = theme_request['data']['contentPage']['sections'][2]['products']['results'] if theme_request['data']['contentPage'] else []
                logging.info('[{}] Found {} products to scan ...'.format(self.provider.upper(), len(tmp_products)))
                [self.products.append(product) for product in tmp_products]
            except:
                logging.warning('[{}] Couldnt parse theme {} ...'.format(self.provider.upper(), theme_url))
        logging.info('[{}] Found a total of {} products ...'.format(self.provider.upper(), len(self.products)))
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()
        self.db.close()

    def _scan_product(self, product):
        set_number = product['productCode']
        title = product['name']
        product_url = '{}{}'.format('https://www.lego.com/de-ch/', product['slug'])
        logging.info("[{}] Scanning product {} ...".format(self.provider.upper(), product_url))
        variantBase = product['variant'] if product.get('variant') else product['variants'][0]
        price = variantBase['price']['centAmount']/100
        currency = variantBase['price']['currencyCode']
        list_price = variantBase['listPrice']['centAmount']/100
        self._update_list_price(set_number, list_price)
        availability = variantBase['attributes']['availabilityStatus']
        logging.info("[{}] Requesting bricklink data for set number {} ...".format(self.provider.upper(), set_number))
        Bricklink(set_number)
        self.p.add_product(set_number, title, price, currency, product_url, availability, self.provider, self.scan_id)

    def _update_list_price(self, set_number, list_price):
        payload = {'data'}
        to_update = self.q._select_query("SELECT id FROM tbl_sets WHERE set_number = %s AND ch_price IS NULL", (set_number, ))
        ids = [s['id'] for s in to_update]
        if ids:
            for set_id in ids:
                update_data = {
                    'table_name' : 'tbl_sets',
                    'data' : {
                        'ch_price' : list_price
                    },
                    'condition' : {
                        'id' : set_id
                    }
                }
                logging.info('[{}] Updating list price ({}) for set number {} ...'.format(self.provider.upper(), list_price, set_number))
                self.db._update_query(update_data)

class Manor(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Manor'

    def init_scan(self):
        base_url = 'https://www.manor.ch/de/shop/spielwaren/lego/c/lego-shop'
        soup = self._get_soup(base_url, self.headers)
        total_pages = int(soup.find('ul', {'class' : 'pagination'}).find('li', text = re.compile(r'[0-9]')).text)
        logging.info("[{}] Found a total pages of {} ...".format(self.provider.upper(), total_pages))
        product_url = 'https://www.manor.ch/Shop/Spielwaren/LEGO/c/lego-shop/getarticleforpage?q=&page={}&sort=top-seller&bv=false'
        for page in range(0, total_pages):
            url = product_url.format(page)
            logging.info("[{}] Requesting {} ...".format(self.provider.upper(), url))
            p_soup = self._get_soup(url, self.headers)
            tmp_products = p_soup.find_all('div', {'class' : 'o-producttile'}) if p_soup else []
            logging.info('[{}] Found {} products to scan ...'.format(self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
        logging.info('[{}] Found a total of {} products ...'.format(self.provider.upper(), len(self.products)))
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()

    def _scan_product(self, product):
        href = product.find('a', {'class' : 'o-producttile__link'})['href']
        product_url = '{}{}'.format('https://www.manor.ch', href)
        logging.info("[{}] Scanning product {} ...".format(self.provider.upper(), product_url))
        title = product.find('div', {'class' : 'o-producttile__copy m-productdetailareaa__areaA__title-line-secondline'}).text.strip()
        set_numbers = self._get_set_numbers_from_string(title)
        price = product.find('span', {'class' : 'js-productprice'}).text.strip()
        for set_number in set_numbers:
            self.p.add_product(set_number, title, price, 'CHF', product_url, None, self.provider, self.scan_id)

class Alternate(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Alternate'

    def init_scan(self):
        base_url = 'https://www.alternate.ch/listing_ajax.xhtml?af=true&listing=0&filterManufacturer=LEGO&q=LEGO&page={}'
        index = 1
        while True:
            url = base_url.format(index)
            logging.info("[{}] Requesting {} ...".format(self.provider.upper(), url))
            soup = self._get_soup(url, self.headers)
            tmp_products = soup.find_all('a', {'class' : 'card align-content-center productBox text-black'}) if soup else []
            if not tmp_products:
                break
            logging.info('[{}] Found {} products to scan ...'.format(self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
            index += 1
        logging.info('[{}] Found a total of {} products ...'.format(self.provider.upper(), len(self.products)))
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()

    def _scan_product(self, product):
        product_url = product['href']
        logging.info("[{}] Scanning product {} ...".format(self.provider.upper(), product_url))
        title = product.find('div', {'class' : 'product-name font-weight-bold'}).text
        price_tag = product.find('span', {'class' : 'price'}).text
        price = self._format_price(price_tag)
        availability = product.find('div', {'class' : 'col-auto delivery-info text-right'}).find('span').text
        availability = re.sub(r' [0-9]+', '', availability)
        set_numbers = self._get_set_numbers_from_string(title)
        for set_number in set_numbers:
            self.p.add_product(set_number, title, price, 'CHF', product_url, availability, self.provider, self.scan_id)

    def _format_price(self, price):
        if ',' in price:
            price = price.replace(',', '.')
        price = float(''.join(re.findall('[0-9.]', price)))
        price = round(price, 2)
        return price

class Techmania(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'Techmania'

    def init_scan(self):
        base_url = 'https://www.techmania.ch/de/Product/List/13278?p={}'
        tmp_products = True
        pageIndex = 1
        while tmp_products:
            url = base_url.format(pageIndex)
            logging.info("[{}] Requesting {} ...".format(self.provider.upper(), url))
            soup = self._get_soup(url, self.headers)
            tmp_products = soup.find_all('div', {'class' : 'c12 lg4 lg-float-l ph-block singleItem productGridElement'}) if soup else []
            tmp_product_urls = ['{}{}'.format('https://www.techmania.ch', item.find('a', {'class' : 'itemBox'})['href']) for item in tmp_products]
            logging.info('[{}] Found {} products to scan ...'.format(self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_product_urls]
            pageIndex += 1
        logging.info('[{}] Found a total of {} products ...'.format(self.provider.upper(), len(self.products)))
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()

    def _scan_product(self, product_url):
        logging.info("[{}] Scanning product {} ...".format(self.provider.upper(), product_url))
        soup = self._get_soup(product_url, self.headers)
        price = soup.find('span', {'itemprop' : 'price'}).text
        price = float(''.join(re.findall('[0-9.]', price)))
        title = soup.find('h1', { 'itemprop' : 'name' }).text
        set_numbers = self._get_set_numbers_from_string(soup.find('span', {'itemprop' : 'identifier'}).text)
        for set_number in set_numbers:
            self.p.add_product(set_number, title, price, 'CHF', product_url, None, self.provider, self.scan_id)

class MeinSpielzeug(ProductScanner):
    def __init__(self):
        ProductScanner.__init__(self)
        self.provider = 'MeinSpielzeug'

    def init_scan(self):
        base_url = 'https://www.meinspielzeug.ch/marke/lego/sortiment/{}'
        soup = self._get_soup(base_url.format(1), self.headers)
        total_pages = soup.find('div', {'class' : 'pageturner'}).find_all('li')[-1].find('a').text
        for page in range(1, int(total_pages)+1):
            url = base_url.format(page)
            logging.info("[{}] Requesting {} ...".format(self.provider.upper(), url))
            soup = self._get_soup(url, self.headers)
            tmp_products = soup.find_all('div', {'class' : 'box-wrapper'}) if soup else []
            logging.info('[{}] Found {} products to scan ...'.format(self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
        logging.info('[{}] Found a total of {} products ...'.format(self.provider.upper(), len(self.products)))
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()

    def _scan_product(self, product):
        href = product.find('a')['href']
        product_url = '{}{}'.format('https://www.meinspielzeug.ch', href)
        logging.info("[{}] Scanning product {} ...".format(self.provider.upper(), product_url))
        title = product.find('h3').text
        article_id = product.find('div', {'class' : 'button'})['data-artikelid']
        price = self._get_price(article_id)
        set_numbers = self._get_set_numbers_from_string(title)
        for set_number in set_numbers:
            self.p.add_product(set_number, title, price, 'CHF', product_url, None, self.provider, self.scan_id)

    def _get_price(self, article_id):
        article_id = 'AN{}'.format(article_id)
        article_url = 'https://aws.meinspielzeug.ch/lagerbestand/{}'.format(article_id)
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
        json = requests.get(url=base_url.format(0), headers=self.headers).json()
        total_pages = json['pagination']['totalPages']
        for page in range(0, total_pages):
            url = base_url.format(page)
            logging.info("[{}] Requesting {} ...".format(self.provider.upper(), url))
            r_json = self._get_json(url=url, headers=self.headers, request_type='get')
            tmp_products = r_json['products'] if r_json else []
            logging.info('[{}] Found {} products to scan ...'.format(self.provider.upper(), len(tmp_products)))
            [self.products.append(product) for product in tmp_products]
        logging.info('[{}] Found a total of {} products ...'.format(self.provider.upper(), len(self.products)))
        [self._scan_product(product) for product in self.products[:_config['scanner']['limit']]]
        self.p.deploy_to_database()
    
    def _scan_product(self, product):
        product_url = '{}{}'.format('https://www.melectronics.ch', product['url'])
        logging.info("[{}] Scanning product {} ...".format(self.provider.upper(), product_url))
        title = product['name']
        set_numbers = self._get_set_numbers_from_string(title)
        price = product['price']['value']
        availability = 'AVAILABLE' if product['orderable'] else 'UNAVAILABLE'
        for set_number in set_numbers:
            self.p.add_product(set_number, title, price, 'CHF', product_url, availability, self.provider, self.scan_id)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s', level=logging.DEBUG)
    # g = Galaxus()
    # g.init_scan()
    # t = Techmania()
    # t.init_scan()
    # ms = MeinSpielzeug()
    # ms.init_scan()
    a = Alternate()
    a.init_scan()
    # mi = Migros()
    # mi.init_scan()
    # l = LEGO()
    # l.init_scan()
    # m = Manor()
    # m.init_scan()
