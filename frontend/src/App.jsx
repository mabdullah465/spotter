import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TripInputForm from './components/TripInputForm';
import HosClocks from './components/HosClocks';
import RouteMap from './components/RouteMap';
import TripSummary from './components/TripSummary';
import DailyLogSheet from './components/DailyLogSheet';
import ItineraryTimeline from './components/ItineraryTimeline';
import HosRulesGuideModal from './components/HosRulesGuideModal';
import SampleTripsModal from './components/SampleTripsModal';
import { planTrip } from './services/api';
import {
  Navigation,
  FileText,
  Clock,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';

export default function App() {
  const [formData, setFormData] = useState({
    current_location: 'Chicago, IL',
    pickup_location: 'Indianapolis, IN',
    dropoff_location: 'Atlanta, GA',
    current_cycle_used: 18.5,
    start_date: new Date().toISOString().slice(0, 10),
    start_time: '07:00',
    carrier_name: 'Spotter Logistics Freight Inc.',
    driver_name: 'Marcus Vance',
    truck_number: 'TRK-8842',
    trailer_number: 'TRL-5390',
    main_office_address: '100 Logistics Blvd, Dallas, TX',
    shipping_documents: 'BOL #984214-SP / General Freight'
  });

  const [tripResult, setTripResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isGuideOpen, setIsGuideOpen] = useState(false);
  const [isSamplesOpen, setIsSamplesOpen] = useState(false);

  // Active Workspace Tab: 'map' | 'logs' | 'itinerary' | 'compliance'
  const [activeTab, setActiveTab] = useState('map');

  // Auto-run trip on initial load
  useEffect(() => {
    executeTripPlan(formData);
  }, []);

  const executeTripPlan = async (dataToSubmit) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const result = await planTrip(dataToSubmit);
      setTripResult(result);
    } catch (err) {
      setErrorMessage(err.message || 'An error occurred while calculating the route and log sheets.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    executeTripPlan(formData);
  };

  const handleSelectSample = (sample) => {
    const updatedData = {
      ...formData,
      current_location: sample.current_location,
      pickup_location: sample.pickup_location,
      dropoff_location: sample.dropoff_location,
      current_cycle_used: sample.current_cycle_used,
      carrier_name: sample.carrier_name || formData.carrier_name,
      driver_name: sample.driver_name || formData.driver_name,
      truck_number: sample.truck_number || formData.truck_number,
      trailer_number: sample.trailer_number || formData.trailer_number,
      shipping_documents: sample.shipping_documents || formData.shipping_documents,
    };
    setFormData(updatedData);
    executeTripPlan(updatedData);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-slate-900 selection:text-white">
      {/* Top Header */}
      <Header
        onOpenGuide={() => setIsGuideOpen(true)}
        onOpenSamples={() => setIsSamplesOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-7 space-y-6">
        {/* Error Alert */}
        {errorMessage && (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-800 flex items-center gap-3 animate-fade-in text-xs">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <div>
              <strong className="font-semibold">Planning Error:</strong> {errorMessage}
            </div>
          </div>
        )}

        {/* Input Form */}
        <TripInputForm
          formData={formData}
          setFormData={setFormData}
          onSubmit={handleFormSubmit}
          isLoading={isLoading}
          onSelectSample={handleSelectSample}
        />

        {/* Results Workspace */}
        {tripResult && (
          <div className="space-y-5 animate-fade-in">
            {/* Workspace Tab Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white border border-slate-200 rounded-lg p-2 shadow-sm">
              <div className="flex items-center gap-1.5 overflow-x-auto">
                <button
                  onClick={() => setActiveTab('map')}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition-colors whitespace-nowrap ${
                    activeTab === 'map'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Navigation className="w-3.5 h-3.5" />
                  <span>Route & Map</span>
                </button>

                <button
                  onClick={() => setActiveTab('logs')}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition-colors whitespace-nowrap ${
                    activeTab === 'logs'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Daily Logs</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${activeTab === 'logs' ? 'bg-slate-800 text-slate-200' : 'bg-slate-100 text-slate-600'}`}>
                    {tripResult.log_sheets?.length || 0}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('itinerary')}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition-colors whitespace-nowrap ${
                    activeTab === 'itinerary'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Clock className="w-3.5 h-3.5" />
                  <span>Itinerary</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${activeTab === 'itinerary' ? 'bg-slate-800 text-slate-200' : 'bg-slate-100 text-slate-600'}`}>
                    {tripResult.timeline?.length || 0}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab('compliance')}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition-colors whitespace-nowrap ${
                    activeTab === 'compliance'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>HOS Clocks & Stats</span>
                </button>
              </div>

              {/* Quick Distance & Drive Time Summary */}
              <div className="flex items-center gap-3 text-xs text-slate-600 px-3 py-1 bg-slate-50 rounded border border-slate-200 font-mono">
                <span>Distance: <strong className="text-slate-900">{tripResult.summary?.total_miles} mi</strong></span>
                <span>•</span>
                <span>Drive Time: <strong className="text-slate-900">{tripResult.summary?.total_driving_hours} hrs</strong></span>
              </div>
            </div>

            {/* TAB 1: ROUTE & MAP */}
            {activeTab === 'map' && (
              <div className="space-y-5">
                <RouteMap routeData={tripResult.route} />
                <TripSummary
                  summary={tripResult.summary}
                  routeData={tripResult.route}
                  logSheetsCount={tripResult.log_sheets?.length || 0}
                />
              </div>
            )}

            {/* TAB 2: DAILY LOG SHEETS (RODS) */}
            {activeTab === 'logs' && tripResult.log_sheets && (
              <DailyLogSheet
                logSheets={tripResult.log_sheets}
                tripSummary={tripResult.summary}
              />
            )}

            {/* TAB 3: ITINERARY TIMELINE */}
            {activeTab === 'itinerary' && tripResult.timeline && (
              <ItineraryTimeline timeline={tripResult.timeline} />
            )}

            {/* TAB 4: HOS COMPLIANCE DIALS & METRICS */}
            {activeTab === 'compliance' && (
              <div className="space-y-5">
                <HosClocks
                  clocks={tripResult.hos_clocks}
                  summary={tripResult.summary}
                />
                <TripSummary
                  summary={tripResult.summary}
                  routeData={tripResult.route}
                  logSheetsCount={tripResult.log_sheets?.length || 0}
                />
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Spotter — FMCSA 49 CFR Part 395 HOS Compliance Engine</span>
          <span>Commercial Motor Vehicle Trip Planning</span>
        </div>
      </footer>

      {/* Modals */}
      <HosRulesGuideModal
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
      />
      <SampleTripsModal
        isOpen={isSamplesOpen}
        onClose={() => setIsSamplesOpen(false)}
        onSelectSample={handleSelectSample}
      />
    </div>
  );
}
