package com.evernym.verity.sdk.protocols.presentproof;

import com.evernym.verity.sdk.utils.AsJsonObject;
import org.json.JSONObject;

import static com.evernym.verity.sdk.utils.JsonUtil.makeArray;

public class Predicate implements AsJsonObject  {
    protected Predicate(String name, int value, Restriction...restrictions) {
        this.data = new JSONObject()
                .put("name", name)
                .put("p_type", ">=")
                .put("p_value", value)
                .put("restrictions", makeArray(restrictions));
    }

    JSONObject data;
    @Override
    public JSONObject toJson() {
        return data;
    }
}
