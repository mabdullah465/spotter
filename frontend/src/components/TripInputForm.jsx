import React, { useState, useRef } from 'react';
import {
  MapPin,
  Clock,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  Calendar,
  Sparkles,
  RotateCcw,
  Plus
} from 'lucide-react';
import { getGeocodeSuggestions } from '../services/api';

export default function TripInputForm({
  formData,
  setFormData,
  onSubmit,
  isLoading
}) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [suggestions, setSuggestions] = useState({ current_location: [], pickup_location: [], dropoff_location: [] });
  const [activeDropdown, setActiveDropdown] = useState(null);

  const debounceTimers = useRef({});

  const handleLocationChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    if (debounceTimers.current[field]) {
      clearTimeout(debounceTimers.current[field]);
    }

    if (value.length >= 2) {
      debounceTimers.current[field] = setTimeout(async () => {
        const results = await getGeocodeSuggestions(value);
        setSuggestions(prev => ({ ...prev, [field]: results }));
        setActiveDropdown(field);
      }, 250);
    } else {
      setSuggestions(prev => ({ ...prev, [field]: [] }));
      setActiveDropdown(null);
    }
  };

  const handleSelectSuggestion = (field, suggestion) => {
    setFormData(prev => ({
      ...prev,
      [field]: suggestion.name || suggestion.display_name
    }));
    setSuggestions(prev => ({ ...prev, [field]: [] }));
    setActiveDropdown(null);
  };

  const handleClearForm = () => {
    setFormData({
      current_location: '',
      pickup_location: '',
      dropoff_location: '',
      current_cycle_used: 0,
      start_date: new Date().toISOString().slice(0, 10),
      start_time: '07:00',
      carrier_name: 'Spotter Logistics Freight Inc.',
      driver_name: '',
      truck_number: '',
      trailer_number: '',
      main_office_address: '',
      shipping_documents: ''
    });
  };

  const presetScenarios = [
    {
      label: 'Coast to Coast (LA → NY)',
      current: 'Los Angeles, CA',
      pickup: 'Dallas, TX',
      dropoff: 'New York, NY',
      cycle: 12.5,
      carrier: 'Trans-America Freight Express',
      driver: 'Marcus Vance',
      truck: 'TRK-9021',
      trailer: 'TRL-4420',
      bol: 'BOL #TA-88921 / Electronics'
    },
    {
      label: 'Midwest Regional (Chicago → Atlanta)',
      current: 'Chicago, IL',
      pickup: 'Indianapolis, IN',
      dropoff: 'Atlanta, GA',
      cycle: 24.0,
      carrier: 'Midwest Intermodal Logistics',
      driver: 'Sarah Jenkins',
      truck: 'TRK-3310',
      trailer: 'TRL-8910',
      bol: 'BOL #MW-55201 / Auto Parts'
    },
    {
      label: 'Tri-State Short Haul (Philly → Baltimore)',
      current: 'Philadelphia, PA',
      pickup: 'Newark, NJ',
      dropoff: 'Baltimore, MD',
      cycle: 8.0,
      carrier: 'Eastern Seaboard Carriers',
      driver: 'David Miller',
      truck: 'TRK-1120',
      trailer: 'TRL-3004',
      bol: 'BOL #ES-10492 / Medical Supplies'
    },
    {
      label: 'Near 70h Cycle Limit (Houston → Nashville)',
      current: 'Houston, TX',
      pickup: 'Memphis, TN',
      dropoff: 'Nashville, TN',
      cycle: 58.5,
      carrier: 'Southern Haulers Inc.',
      driver: 'Robert Taylor',
      truck: 'TRK-7740',
      trailer: 'TRL-6612',
      bol: 'BOL #SH-40912 / Building Materials'
    }
  ];

  const applyPreset = (preset) => {
    setFormData(prev => ({
      ...prev,
      current_location: preset.current,
      pickup_location: preset.pickup,
      dropoff_location: preset.dropoff,
      current_cycle_used: preset.cycle,
      carrier_name: preset.carrier,
      driver_name: preset.driver,
      truck_number: preset.truck,
      trailer_number: preset.trailer,
      shipping_documents: preset.bol
    }));
  };

  const remainingCycle = Math.max(0, 70 - Number(formData.current_cycle_used || 0)).toFixed(1);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 sm:p-7 shadow-sm">
      {/* Header & Quick Action Buttons */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pb-5 border-b border-slate-100">
        <div>
          <h2 className="text-base font-semibold text-slate-900">
            Trip Parameters
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Type any custom origin, pickup, and delivery address, or select a sample preset below.
          </p>
        </div>

        {/* Quick Presets & Clear Button */}
        <div className="flex items-center flex-wrap gap-1.5 text-xs text-slate-600">
          <button
            type="button"
            onClick={handleClearForm}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium border border-slate-200 transition-colors"
          >
            <RotateCcw className="w-3 h-3 text-slate-500" />
            <span>Clear / New Trip</span>
          </button>
          
          <span className="text-[11px] text-slate-400 font-medium ml-1 mr-0.5">Presets:</span>
          {presetScenarios.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPreset(p)}
              className="px-2.5 py-1 rounded bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs transition-colors font-medium border border-slate-200"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={onSubmit} className="mt-6 space-y-5">
        {/* Route Stops Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Current Location */}
          <div className="relative">
            <label className="block text-xs font-medium text-slate-700 mb-1.5">
              1. Current Location (Start)
            </label>
            <div className="relative">
              <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
              <input
                type="text"
                required
                value={formData.current_location}
                onChange={(e) => handleLocationChange('current_location', e.target.value)}
                placeholder="e.g. Seattle, WA or Address"
                className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors"
              />
            </div>

            {/* Suggestions */}
            {activeDropdown === 'current_location' && suggestions.current_location?.length > 0 && (
              <ul className="absolute z-50 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-48 overflow-y-auto text-xs py-1 divide-y divide-slate-100">
                {suggestions.current_location.map((s, idx) => (
                  <li
                    key={idx}
                    onClick={() => handleSelectSuggestion('current_location', s)}
                    className="px-3 py-2 hover:bg-slate-50 text-slate-700 cursor-pointer flex items-center gap-2"
                  >
                    <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    <span className="truncate">{s.display_name || s.name}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Pickup Location */}
          <div className="relative">
            <label className="block text-xs font-medium text-slate-700 mb-1.5 flex items-center justify-between">
              <span>2. Pickup (Shipper)</span>
              <span className="text-[11px] text-slate-500 font-normal">1 hr loading</span>
            </label>
            <div className="relative">
              <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
              <input
                type="text"
                required
                value={formData.pickup_location}
                onChange={(e) => handleLocationChange('pickup_location', e.target.value)}
                placeholder="e.g. Denver, CO or Address"
                className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors"
              />
            </div>

            {/* Suggestions */}
            {activeDropdown === 'pickup_location' && suggestions.pickup_location?.length > 0 && (
              <ul className="absolute z-50 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-48 overflow-y-auto text-xs py-1 divide-y divide-slate-100">
                {suggestions.pickup_location.map((s, idx) => (
                  <li
                    key={idx}
                    onClick={() => handleSelectSuggestion('pickup_location', s)}
                    className="px-3 py-2 hover:bg-slate-50 text-slate-700 cursor-pointer flex items-center gap-2"
                  >
                    <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    <span className="truncate">{s.display_name || s.name}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Dropoff Location */}
          <div className="relative">
            <label className="block text-xs font-medium text-slate-700 mb-1.5 flex items-center justify-between">
              <span>3. Dropoff (Consignee)</span>
              <span className="text-[11px] text-slate-500 font-normal">1 hr unloading</span>
            </label>
            <div className="relative">
              <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
              <input
                type="text"
                required
                value={formData.dropoff_location}
                onChange={(e) => handleLocationChange('dropoff_location', e.target.value)}
                placeholder="e.g. Miami, FL or Address"
                className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-slate-900 transition-colors"
              />
            </div>

            {/* Suggestions */}
            {activeDropdown === 'dropoff_location' && suggestions.dropoff_location?.length > 0 && (
              <ul className="absolute z-50 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-48 overflow-y-auto text-xs py-1 divide-y divide-slate-100">
                {suggestions.dropoff_location.map((s, idx) => (
                  <li
                    key={idx}
                    onClick={() => handleSelectSuggestion('dropoff_location', s)}
                    className="px-3 py-2 hover:bg-slate-50 text-slate-700 cursor-pointer flex items-center gap-2"
                  >
                    <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    <span className="truncate">{s.display_name || s.name}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Schedule & Cycle Hours */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
          {/* Current Cycle Used */}
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
            <div className="flex items-center justify-between text-xs font-medium text-slate-700 mb-2">
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                Current Cycle Used
              </span>
              <span className="font-mono font-semibold text-slate-900">{formData.current_cycle_used || 0} hrs</span>
            </div>
            <input
              type="range"
              min="0"
              max="70"
              step="0.5"
              value={formData.current_cycle_used || 0}
              onChange={(e) => setFormData(p => ({ ...p, current_cycle_used: parseFloat(e.target.value) || 0 }))}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
            />
            <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
              <span>70hr / 8-day rule</span>
              <span>Available: <strong className="text-slate-900 font-mono">{remainingCycle} hrs</strong></span>
            </div>
          </div>

          {/* Departure Date */}
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
            <label className="block text-xs font-medium text-slate-700 mb-2 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              Departure Date
            </label>
            <input
              type="date"
              value={formData.start_date || new Date().toISOString().slice(0, 10)}
              onChange={(e) => setFormData(prev => ({ ...prev, start_date: e.target.value }))}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900 font-mono"
            />
          </div>

          {/* Departure Time */}
          <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
            <label className="block text-xs font-medium text-slate-700 mb-2 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              Departure Time
            </label>
            <input
              type="time"
              value={formData.start_time || '07:00'}
              onChange={(e) => setFormData(prev => ({ ...prev, start_time: e.target.value }))}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900 font-mono"
            />
          </div>
        </div>

        {/* Collapsible Carrier Info */}
        <div className="pt-1">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 font-medium transition-colors"
          >
            {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            <span>{showAdvanced ? 'Hide Carrier & Log Details' : 'Carrier & Vehicle Details (Optional)'}</span>
          </button>

          {showAdvanced && (
            <div className="mt-3 p-4 rounded-lg bg-slate-50 border border-slate-200 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs animate-fade-in">
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Carrier Name</label>
                <input
                  type="text"
                  value={formData.carrier_name || ''}
                  onChange={(e) => setFormData(p => ({ ...p, carrier_name: e.target.value }))}
                  placeholder="Spotter Logistics Freight Inc."
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Driver Name</label>
                <input
                  type="text"
                  value={formData.driver_name || ''}
                  onChange={(e) => setFormData(p => ({ ...p, driver_name: e.target.value }))}
                  placeholder="Marcus Vance"
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Tractor / Truck #</label>
                <input
                  type="text"
                  value={formData.truck_number || ''}
                  onChange={(e) => setFormData(p => ({ ...p, truck_number: e.target.value }))}
                  placeholder="TRK-8842"
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Trailer #</label>
                <input
                  type="text"
                  value={formData.trailer_number || ''}
                  onChange={(e) => setFormData(p => ({ ...p, trailer_number: e.target.value }))}
                  placeholder="TRL-5390"
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Main Office Address</label>
                <input
                  type="text"
                  value={formData.main_office_address || ''}
                  onChange={(e) => setFormData(p => ({ ...p, main_office_address: e.target.value }))}
                  placeholder="100 Logistics Blvd, Dallas, TX"
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-600 mb-1">Shipping Docs / BOL</label>
                <input
                  type="text"
                  value={formData.shipping_documents || ''}
                  onChange={(e) => setFormData(p => ({ ...p, shipping_documents: e.target.value }))}
                  placeholder="BOL #984214-SP / General Freight"
                  className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-slate-900"
                />
              </div>
            </div>
          )}
        </div>

        {/* Primary Action Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 px-5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Planning Trip & Generating Log Sheets...</span>
              </>
            ) : (
              <>
                <span>Calculate Trip & Draw Daily Logs</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
