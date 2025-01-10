const fs = require("fs");

// Read the JSON data from schema.json
fs.readFile("schema.json", "utf8", (err, jsonString) => {
  if (err) {
    console.log("Error reading file from disk:", err);
    return;
  }
  try {
    function resolveReference(refPath) {
      const parts = refPath.split("/").slice(1);
      const ref = parts.reduce((obj, key) => obj[key], data);
      ref[`${parts[0]}_key`] = parts[parts.length - 1];
      return ref;
    }

    function recursiveResolveReferences(obj) {
      if (Array.isArray(obj)) {
        obj.forEach((item) => {
          recursiveResolveReferences(item);
        });
      } else if (obj !== null && typeof obj === "object") {
        if ("$ref" in obj) {
          const referencedObj = resolveReference(obj["$ref"]);
          delete obj["$ref"];
          Object.assign(obj, referencedObj);
        }
        Object.values(obj).map(recursiveResolveReferences);
      }
    }

    function flattenUiSchema(fieldset) {
      if (fieldset["ui:schema"] == null) {
        return fieldset;
      }

      const newFieldset = JSON.parse(JSON.stringify(fieldset));
      if (fieldset["ui:schema"]["ui:field_type"] !== undefined) {
        newFieldset["ui:schema.ui:field_type"] =
          newFieldset["ui:schema"]["ui:field_type"];
        delete newFieldset["ui:schema"]["ui:field_type"];
      }
      if (newFieldset["ui:schema"]["ui:options"] !== undefined) {
        newFieldset["ui:schema.ui:options"] =
          newFieldset["ui:schema"]["ui:options"];
        delete newFieldset["ui:schema"]["ui:options"];
      }
      if (newFieldset["ui:schema"]["items"]) {
        if (newFieldset["ui:schema"]["items"]["ui:options"] !== undefined) {
          newFieldset["ui:schema.items.ui:options"] =
            newFieldset["ui:schema"]["items"]["ui:options"];
          delete newFieldset["ui:schema"]["items"]["ui:options"];
        }
        if (newFieldset["ui:schema"]["items"]["ui:field_type"] !== undefined) {
          newFieldset["ui:schema.items.ui:field_type"] =
            newFieldset["ui:schema"]["items"]["ui:field_type"];
          delete newFieldset["ui:schema"]["items"]["ui:field_type"];
        }
        for (const [key, value] of Object.entries(
          newFieldset["ui:schema"]["items"]
        )) {
          if (key in newFieldset["items"]["properties"]) {
            newFieldset["items"]["properties"][key] = {
              ...value,
              ...newFieldset["items"]["properties"][key],
            };
          } else {
            console.log(
              `${key} does not exist in items - handle this edge case`,
              {
                key,
                value,
              }
            );
          }
        }
        delete newFieldset["ui:schema"]["items"];
      }

      if (Object.keys(newFieldset["ui:schema"]).length !== 0) {
        console.log("fields still remain in ui:schema", { fieldset });
      }
      delete newFieldset["ui:schema"];
      return newFieldset;
    }

    const data = JSON.parse(jsonString);

    // extract out pages to root level
    data["pages"] = JSON.parse(JSON.stringify(data["ui:layout"]["pages"]));
    delete data["ui:layout"];

    // resolve properties references first since $ref may exist for definitions
    recursiveResolveReferences(data.properties, data);
    recursiveResolveReferences(data.pages, data);
    delete data.properties;
    delete data.definitions;

    data.pages = data.pages.map((p) => {
      if ("fieldsets" in p) {
        const fieldsets = p.fieldsets.map(flattenUiSchema);
        p.fieldsets = fieldsets;
      }
      return p;
    });

    // Save the updated JSON data to a file
    fs.writeFile(
      "schema-dereferenced.json",
      JSON.stringify(data, null, 2),
      (err) => {
        if (err) throw err;
        console.log('JSON data saved to "updated_schema.json"');
      }
    );
  } catch (err) {
    console.log("Error parsing JSON string:", err);
  }
});
