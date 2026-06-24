export default function InboundLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-[calc(100vh)] max-h-[calc(100vh)] flex-col overflow-hidden">
      {children}
    </div>
  );
}
