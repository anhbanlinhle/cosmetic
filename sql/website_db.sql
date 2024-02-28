create table cosmetic.website
(
    id                int auto_increment
        primary key,
    url               varchar(255) null comment 'link to website',
    product_suffix    char(100)    null comment 'link to product category',
    ingredient_suffix char(100)    null comment 'link to ingredient category',
    preg_suffix       char(100)    null comment 'link to ingredient pregnancy validation category'
);

create table cosmetic.content_list_xpath
(
    id         int auto_increment
        primary key,
    website_id int                                    not null,
    type       enum ('PRODUCT', 'INGREDIENT', 'PREG') null,
    path       text                                   null,
    constraint content_list_xpath_ibfk_1
        foreign key (website_id) references cosmetic.website (id)
);

create index website_id
    on cosmetic.content_list_xpath (website_id);

create table cosmetic.ingredient
(
    id                    int auto_increment
        primary key,
    website_id            int          not null,
    name_xpath            varchar(255) null,
    description_xpath     text         null,
    related_document      varchar(255) null,
    xpath_to_product_list varchar(255) null,
    constraint ingredient_ibfk_1
        foreign key (website_id) references cosmetic.website (id)
            on delete cascade
);

create index website_id
    on cosmetic.ingredient (website_id);

create table cosmetic.product
(
    id                       int auto_increment
        primary key,
    website_id               int          not null,
    brand_xpath              varchar(255) null,
    name_xpath               varchar(255) null,
    description_xpath        varchar(500) null,
    xpath_to_ingredient_list varchar(255) null,
    description_expand       varchar(255) null,
    constraint product_ibfk_1
        foreign key (website_id) references cosmetic.website (id)
            on delete cascade
);

create index website_id
    on cosmetic.product (website_id);

insert into cosmetic.website (id, url, product_suffix, ingredient_suffix, preg_suffix)
values  (1, 'https://incidecoder.com', '/search/product?query=', 'ingredients', null),
        (2, 'https://callmeduy.com/', 'san-pham/', 'thanh-phan/', null),
        (3, 'https://guo.vn/', 'san-pham/', 'thanh-phan-my-pham/', 'tra-cuu-thanh-phan-my-pham-cho-ba-bau/');

insert into cosmetic.content_list_xpath (id, website_id, type, path)
values  (1, 1, 'PRODUCT', '//*[@id="content"]//*[contains(@class, "searchpage")]/*/a[starts-with(@href, "/products/")]'),
        (2, 3, 'PREG', '//*[@id="content"]//*[@class="wpb_column vc_column_container vc_col-sm-3"]//*[contains(@class, "wpb_text_column wpb_content_element  vc_custom_")]/parent::*//*[@class="wpb_wrapper"]/*[name()=''div'' or name()=''span'' or name()=''p'']'),
        (3, 3, 'PRODUCT', '//*[contains(@id, "container")]//*[@id="primary"]//*[@id="content"]//*[contains(@class, "entry-content")]//*[contains(@class, "wpb_column vc_column_container vc_col-sm-9")]//ul//a[contains(@href, ''/san-pham/'')]'),
        (4, 3, 'INGREDIENT', '//*[contains(@id, "container")]//*[@id="primary"]//*[@id="content"]//*[contains(@class, "entry-content")]//*[contains(@class, "normal_height vc_row wpb_row vc_row-fluid vc_custom_1654140385317 vc_row-o-content-top vc_row-flex")]//a');

insert into cosmetic.product (id, website_id, brand_xpath, name_xpath, description_xpath, xpath_to_ingredient_list, description_expand)
values  (1, 1, '//*[@id="product-brand-title"]//*', '//*[@id="product-title"]', '//*[@id="product-details"]', '//*[@id="ingredlist-short"]//*[@id="showmore-section-ingredlist-short"]//*[contains(@role,"listitem")]/a', '//*[name()=''div'' or name()=''span'' or name()=''p''][text()]'),
        (2, 3, null, '//*[contains(@id, "container")]//*[@id="primary"]//*[@id="content"]//*[contains(@class, "product_info")]//*[contains(@class, "product_title")]', '//*[contains(@id, "container")]//*[@id="primary"]//*[@id="content"]//*[contains(@class, "single-post-content")]//*[contains(@class, "wpb_column vc_column_container vc_col-sm-12")]//*[contains(@class, "wpb_wrapper")]//*[contains(@class, "wpb_wrapper")]/div/preceding-sibling::*[name()!=''div'']', '//*[contains(@id, "container")]//*[@id="primary"]//*[@id="content"]//*[@id="tab-thong-so-san-pham"]//table/tbody//td//*[starts-with(text(), "Thành ")]/parent::*/following-sibling::td', '');

insert into cosmetic.ingredient (id, website_id, name_xpath, description_xpath, related_document, xpath_to_product_list)
values  (1, 1, '{"name": "//*[@id=''content'']//*[contains(@class, ''ingredinfobox'')]//h1", "alias": "//*[@id=''content'']//*[contains(@class, ''ingredinfobox'')]//*[contains(text(), ''called'')]/following-sibling::*[text()]"}', '//*[@id="content"]//*[@id="details"]//*[@id="showmore-section-details"]//*[contains(@class, "content")]//*[name()=''li'' or name()=''span'' or name()=''p''][text()]', '//*[@id="proof"]/*[@id="showmore-section-proof"]//*[name()=''li'' or name()=''span'' or name()=''p''][text()]', '//*[@id="content"]//*[contains(@id, "product")]//a[starts-with(@href, "/product")]'),
        (2, 3, '//*[contains(@id, "container")]//*[@id="primary"]//*[@id="content"]//h1[contains(@class, "title")]', '{ "description": "//*[(name() = ''b'' or name() = ''strong'') and contains(text(), ''Mô tả'')]/following-sibling::text()", "safe_for_preg": "//*[contains(text(), ''Đánh giá thành phần cho bà bầu'')]/following-sibling::text() | //*[contains(text(), ''Đánh giá thành phần cho bà bầu'')]/following-sibling::span/text()" }', null, null);
