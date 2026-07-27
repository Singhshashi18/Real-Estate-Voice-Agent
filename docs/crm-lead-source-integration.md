# CRM Lead Source Integration

## Objective
Integrate CRM-originated lead sources into the voice-agent pipeline so each inbound/outbound conversation can be traced to a campaign and source channel.

## Proposed Data Contract

### Lead Source Fields
- `crm_lead_id`: unique lead identifier from CRM
- `lead_source`: high-level source (e.g., portal, referral, ad campaign)
- `lead_source_detail`: optional sub-source/campaign name
- `ingested_at`: ISO timestamp for ingestion

### Conversation Metadata Fields
- `call_id`: provider call/session identifier
- `agent_mode`: `inbound` or `outbound`
- `property_interest`: optional normalized intent tag
- `follow_up_required`: boolean

## Integration Flow
1. Receive lead payload from CRM webhook/export.
2. Validate required source fields and normalize values.
3. Attach lead-source context when starting voice sessions.
4. Persist mapped metadata for reporting and conversion tracking.
5. Emit event logs for downstream analytics.

## Validation Rules
- Reject leads missing `crm_lead_id` or `lead_source`.
- Normalize lead source labels to canonical values.
- Preserve original source text in `lead_source_detail`.

## Next Implementation Steps
- Add CRM payload schema in backend validation layer.
- Extend call/session persistence model with lead-source columns.
- Include lead-source metadata in outbound call batch jobs.
- Add dashboard filters for lead-source attribution.
