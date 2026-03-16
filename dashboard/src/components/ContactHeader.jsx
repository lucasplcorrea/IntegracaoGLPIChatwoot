export function ContactHeader({ contactId, history, profile }) {
  // Derive contact info from Chatwoot profile (if available) or the first history entry
  const name = profile?.name ?? history?.[0]?.contact_name ?? `Contato #${contactId ?? "–"}`;
  const initial = name !== `Contato #${contactId}` ? name.slice(0, 2).toUpperCase() : "?";
  
  const email = profile?.email;
  const phone = profile?.phone_number;

  return (
    <div className="contact-header">
      <div className="contact-avatar">
        {profile?.thumbnail ? <img src={profile.thumbnail} alt={name} /> : initial}
      </div>
      <div className="contact-info">
        <div className="contact-name">{name}</div>
        <div className="contact-meta">
          ID: {contactId ?? "–"}
          {email && ` • ${email}`}
          {phone && ` • ${phone}`}
        </div>
      </div>
    </div>
  );
}
