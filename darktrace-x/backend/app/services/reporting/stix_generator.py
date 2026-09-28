import uuid
from typing import Dict, Any, List
from datetime import datetime

class Stix21BundleGenerator:
    """
    STIX 2.1 Standardized Cyber Threat Intelligence Exporter.
    Translates DARKTRACE-X actors, indicators, infrastructure,
    campaigns, and relationships into OASIS STIX 2.1 JSON specifications.
    """

    def generate_bundle(
        self,
        actor: Dict[str, Any],
        personas: List[Dict[str, Any]],
        indicators: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        campaign: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Builds a valid STIX 2.1 bundle object.
        """
        bundle_id = f"bundle--{uuid.uuid4()}"
        now_stix = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        objects = []

        # 1. Threat Actor SDO
        threat_actor_id = f"threat-actor--{uuid.uuid5(uuid.NAMESPACE_DNS, str(actor.get('id')))}"
        threat_actor = {
            "type": "threat-actor",
            "spec_version": "2.1",
            "id": threat_actor_id,
            "created": now_stix,
            "modified": now_stix,
            "name": actor.get("primary_name", "Unknown Actor"),
            "description": actor.get("summary", ""),
            "threat_actor_types": [actor.get("threat_category", "unknown").lower().replace(" ", "-")],
            "aliases": [p.get("canonical_handle") for p in personas if p.get("canonical_handle")],
            "confidence": int(actor.get("confidence_score", 0.7) * 100),
            "labels": ["dark-web-threat-actor", "de-anonymized-persona"],
            "custom_properties": {
                "x_darktrace_id": actor.get("id"),
                "x_threat_level": actor.get("threat_level")
            }
        }
        objects.append(threat_actor)

        # 2. Campaign SDO (if present)
        if campaign:
            campaign_id = f"campaign--{uuid.uuid5(uuid.NAMESPACE_DNS, str(campaign.get('id', 'cmp-1')))}"
            objects.append({
                "type": "campaign",
                "spec_version": "2.1",
                "id": campaign_id,
                "created": now_stix,
                "modified": now_stix,
                "name": campaign.get("name", "Darknet Operation"),
                "description": campaign.get("description", ""),
                "first_seen": now_stix,
                "confidence": int(campaign.get("confidence", 0.8) * 100)
            })
            # Attributed-to relationship
            objects.append({
                "type": "relationship",
                "spec_version": "2.1",
                "id": f"relationship--{uuid.uuid4()}",
                "created": now_stix,
                "modified": now_stix,
                "relationship_type": "attributed-to",
                "source_ref": campaign_id,
                "target_ref": threat_actor_id
            })

        # 3. Indicators (Wallets, Domains, IPs, Hashes)
        for ind in indicators:
            ind_type = ind.get("type", "indicator")
            ind_val = ind.get("value", "")
            indicator_id = f"indicator--{uuid.uuid4()}"

            pattern = f"[ipv4-addr:value = '{ind_val}']" if ind_type == "IP" else f"[domain-name:value = '{ind_val}']"

            objects.append({
                "type": "indicator",
                "spec_version": "2.1",
                "id": indicator_id,
                "created": now_stix,
                "modified": now_stix,
                "name": f"{ind_type}: {ind_val}",
                "pattern_type": "stix",
                "pattern": pattern,
                "valid_from": now_stix,
                "labels": ["dark-web-indicator", ind_type.lower()]
            })

            # Relationship: indicates
            objects.append({
                "type": "relationship",
                "spec_version": "2.1",
                "id": f"relationship--{uuid.uuid4()}",
                "created": now_stix,
                "modified": now_stix,
                "relationship_type": "indicates",
                "source_ref": indicator_id,
                "target_ref": threat_actor_id
            })

        return {
            "type": "bundle",
            "id": bundle_id,
            "objects": objects
        }

stix_generator = Stix21BundleGenerator()
