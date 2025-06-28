import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FileText, ArrowRight, Zap, Shield, Download } from "lucide-react";

const Index = () => {
  const handleStartFormatting = () => {
    // Use Flask URL if available, fallback to categoriser
    const categoryUrl = (window as any).flaskUrls?.category || '/categoriser';
    window.location.href = categoryUrl;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-white">
      {/* Header */}
      <header className="px-6 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-semibold text-slate-900">DimePrep</h1>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="px-6 pb-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-8">
              <Zap className="w-4 h-4 mr-2" />
              Must-Have Finance Tool
            </div>
            
            <h2 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6 leading-tight">
              Simple, intuitive
              <br />
              <span className="text-blue-600 relative">
                CSV formatting
                <div className="absolute bottom-2 left-0 right-0 h-1 bg-blue-200 rounded-full"></div>
              </span>
            </h2>
            
            <p className="text-xl text-slate-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              Transform your bank CSV statements into Dime-ready formats. 
              Clean, accurate, and effortless financial data preparation.
            </p>

            <Button 
              onClick={handleStartFormatting}
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-2xl text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 group"
            >
              Start formatting!
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center mb-6">
                  <Download className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">
                  Instant Processing
                </h3>
                <p className="text-slate-600 leading-relaxed">
                  Upload your bank CSV and get a Dime-ready file in seconds. No waiting, no hassle.
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-purple-100 rounded-2xl flex items-center justify-center mb-6">
                  <Shield className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">
                  Secure & Private
                </h3>
                <p className="text-slate-600 leading-relaxed">
                  Your financial data stays private. All processing happens locally in your browser.
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-sm hover:shadow-md transition-shadow duration-200">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">
                  Perfect Formatting
                </h3>
                <p className="text-slate-600 leading-relaxed">
                  Automatically formats columns, dates, and amounts to match Dime's requirements.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* CTA Section */}
          <div className="bg-slate-900 rounded-3xl p-12 text-center">
            <h3 className="text-3xl font-bold text-white mb-4">
              Ready to streamline your finances?
            </h3>
            <p className="text-slate-300 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands of users who trust DimePrep to prepare their financial data with precision and ease.
            </p>
            <Button 
              onClick={handleStartFormatting}
              size="lg"
              variant="secondary"
              className="bg-white text-slate-900 hover:bg-slate-100 px-8 py-4 rounded-2xl text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Get Started Now
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;