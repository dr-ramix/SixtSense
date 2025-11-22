export default function HomePage() {
  return (
    <div className="flex min-h-screen w-full">
      {/* Left side - Chatbot */}
      <div className="w-1/2 border-r p-6 flex items-center justify-center bg-gray-50">
        <div className="text-2xl font-semibold">Chatbot</div>
      </div>

      {/* Right side - Cars */}
      <div className="w-1/2 p-6 flex items-center justify-center bg-white">
        <div className="text-2xl font-semibold">Cars</div>
      </div>
    </div>
  );
}
