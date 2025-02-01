import xmlrpc.client
import logging

logging.basicConfig(
    filename="attr_not_add.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

url_12 = "http://0.0.0.0:8075"
db_12 = "demo"
username_12 = "demo"
password_12 = "demo"

url_18 = "http://0.0.0.0:8069"
db_18 = "demo"
username_18 = "demo"
password_18 = "demo"

# Authenticate Odoo 12
common12 = xmlrpc.client.ServerProxy(f"{url_12}/xmlrpc/2/common")
uid_12 = common12.authenticate(db_12, username_12, password_12, {})

# Authenticate Odoo 18
common18 = xmlrpc.client.ServerProxy(f"{url_18}/xmlrpc/2/common")
uid_18 = common18.authenticate(db_18, username_18, password_18, {})

if uid_12 and uid_18:
    models_12 = xmlrpc.client.ServerProxy(f"{url_12}/xmlrpc/2/object")
    models_18 = xmlrpc.client.ServerProxy(f"{url_18}/xmlrpc/2/object")

    # Search and read all individual partners from Odoo 12
    product_ids = models_12.execute_kw(
        db_12,
        uid_12,
        password_12,
        "product.template",
        "search_read",
        [[("attribute_line_ids", "!=", False)]],
        {"fields": ["name", "attribute_line_ids"]},
    )

    if product_ids:
        for data in product_ids:
            for line_id in data["attribute_line_ids"]:
                attribute_line_ids = models_12.execute_kw(
                    db_12,
                    uid_12,
                    password_12,
                    "product.template.attribute.line",
                    "read",
                    [line_id],
                )

                for values_id in attribute_line_ids:
                    attribute_line_values_ids = models_12.execute_kw(
                        db_12,
                        uid_12,
                        password_12,
                        "product.template.attribute.value",
                        "search_read",
                        [
                            [
                                ("id", "in", values_id["product_template_value_ids"]),
                                ("price_extra",'>',0.0),
                            ]
                        ],
                    )

                    for values_line in attribute_line_values_ids:

                        product_news = models_18.execute_kw(
                            db_18,
                            uid_18,
                            password_18,
                            "product.template",
                            "search_read",
                            [[("name", "=", values_line["product_tmpl_id"][1])]],
                            {"fields": ["name", "attribute_line_ids"]},
                        )

                        for newProduct in product_news:
                            if len(newProduct['attribute_line_ids'])>0:

                                new_attribute_line_values_ids = models_18.execute_kw(
                                    db_18,
                                    uid_18,
                                    password_18,
                                    "product.template.attribute.value",
                                    "search",
                                    [
                                        [
                                            (
                                                "product_tmpl_id",
                                                "=",
                                                newProduct["id"],
                                            ),
                                            ("name", "=", values_line['name']),
                                        ]
                                    ],
                                )

                                if len(new_attribute_line_values_ids) > 0:
                                    for new_att_value_id in new_attribute_line_values_ids:
                                        models_18.execute_kw(
                                            db_18,
                                            uid_18,
                                            password_18,
                                            "product.template.attribute.value",
                                            "write",
                                            [
                                                new_att_value_id,
                                                {
                                                    "price_extra": values_line[
                                                        "price_extra"
                                                    ],
                                                },
                                            ],
                                        )
                                        print("done")
                                else:
                                    logging.info(data)
else:
    print("Authentication failed for one or both instances.")
