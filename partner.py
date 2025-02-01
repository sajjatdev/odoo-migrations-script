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
    partner_ids = models_12.execute_kw(
        db_12,
        uid_12,
        password_12,
        "res.partner",
        "search",
        [[("is_company", "=", True)]],
    )

    for partner_id in partner_ids:
        try:
            # Read partner data
            partner_data = models_12.execute_kw(
                db_12, uid_12, password_12, "res.partner", "read", [partner_id]
            )[0]

            country_id = False
            if partner_data.get("country_id"):
                country_name = partner_data["country_id"][1]
                country_ids = models_18.execute_kw(
                    db_18,
                    uid_18,
                    password_18,
                    "res.country",
                    "search",
                    [[("name", "=", country_name)]],
                )
                country_id = country_ids[0] if country_ids else False

            # Resolve state
            state_id = False
            if partner_data.get("state_id"):
                state_name = partner_data["state_id"][1]
                state_ids = models_18.execute_kw(
                    db_18,
                    uid_18,
                    password_18,
                    "res.country.state",
                    "search",
                    [[("name", "=", state_name)]],
                )
                state_id = state_ids[0] if state_ids else False

            category_id = []

            if len(partner_data.get("category_id")) > 0:
                category_ids = models_12.execute_kw(
                    db_12,
                    uid_12,
                    password_12,
                    "res.partner.category",
                    "read",
                    partner_data["category_id"],
                    {"fields": ["name"]},
                )
                for names in category_ids:

                    category_id_new = models_18.execute_kw(
                        db_18,
                        uid_18,
                        password_18,
                        "res.partner.category",
                        "search",
                        [[("name", "=", names["name"])]],
                    )
                    if len(category_id_new) > 0:
                        category_id.append(category_id_new[0])

            new_partner_data = {
                "name": partner_data["name"],
                "street": partner_data.get("street", ""),
                "city": partner_data.get("city", ""),
                "state_id": state_id,
                "country_id": country_id,
                "zip": partner_data.get("zip", ""),
                "phone": partner_data.get("phone", ""),
                "email": partner_data.get("email", ""),
                "website": partner_data.get("website", ""),
                "vat": partner_data.get("vat", ""),
                "image_1920": partner_data.get("image", ""),
                "is_company": True,
                "comment": partner_data.get("comment", ""),
                "lang": partner_data["lang"],
                "is_vandor": partner_data["supplier"],
                "supplier_discount": partner_data["supplier_discount"],
                "category_id": [(6, 0, category_id)],
            }

            new_partner_id = models_18.execute_kw(
                db_18,
                uid_18,
                password_18,
                "res.partner",
                "create",
                [new_partner_data],
            )
            print(f"New partner created with ID: {new_partner_id}")

        except Exception as e:
            logging.info(partner_id)

else:
    print("Authentication failed for one or both instances.")
