import { useState } from "react";
import UploadForm from "../components/UploadForm";
import ClusterChart from "../components/ClusterChart";
import { fetchClusters } from "../services/api";

export default function Dashboard() {
  const [data, setData] = useState(null);

  const handleUpload = async (file) => {
    const result = await fetchClusters(file);
    console.log("Backend response:", result); // ✅ helps debug
    setData(result);
  };

  return (
    <div>
      <h1>Customer Segmentation Dashboard</h1>
      <UploadForm onUpload={handleUpload} />
      {data && <ClusterChart data={data} />}
    </div>
  );
}
