import { Card, Flex, Icon, Badge } from "@chakra-ui/react";
import { CheckCircleIcon, XCircleIcon, HourglassIcon } from "@chakra-ui/icons";
import type { SubmissionResultItem } from "@/types/api";

interface SubmissionSummaryProps {
  /** Results of inventory submission */
  results: SubmissionResultItem[];
  /** Callback to navigate to inventory */
  onViewInventory: () => void;
  /** Callback to reset scanning */
  onScanAnother: () => void;
}

export default function SubmissionSummary({
  results,
  onViewInventory,
  onScanAnother,
}: SubmissionSummaryProps) {
  /* Count categories */
  const addedCount = results.filter(r => r.status === "added").length;
  const skippedCount = results.filter(r => r.status === "skipped").length;
  const failedCount = results.filter(r => r.status === "failed").length;

  const overallStatus = results.length === 0 ? "no-data" :
    addedCount > 0 && skippedCount === 0 && failedCount === 0 ? "success" :
    failedCount > 0 ? "failed" : "partial";

  /* Get status badge color */
  const getStatusColor = (status: string) => {
    switch (status) {
      case "added": return "success";
      case "skipped": return "amber";
      case "failed": return "red";
      default: return "default";
    }
  };

  /* Overall summary text */
  const summaryText = `${addedCount} added, ${skippedCount} skipped, ${failedCount} failed`;

  return (
    <Card
      variant="outline"
      colorScheme={getStatusColor(overallStatus)}
     maxW="sm"
     mt={4}
     mb={4}
     borderRadius="lg"
    >
      <Flex justify="center" align="center" mb={2}>
        <Icon as={overallStatus === "success" ? CheckCircleIcon : overallStatus === "failed" ? XCircleIcon : HourglassIcon}
          color="inherit"
          size={24} />
      </Flex>

      <Flex justify="center" space-y-1>
        <Badge colorScheme={getStatusColor(overallStatus)} textStyle="lg">
          {summaryText}
        </Badge>
      </Flex>

      {/* Detailed results */}
      <Flex flexDirection="column" space-y-2 mt={2}>
        {results.map((result) => {
          const isSuccess = result.status === "added";
          const isSkipped = result.status === "skipped";
          const isFailed = result.status === "failed";

          return (
            <Flex items-start space-y-1 text-sm>
              <Badge
                as="span"
                colorScheme={getStatusColor(result.status)}
                size="md"
                ml={1}
                pl={1}
              >
                {result.status === "added" ? CheckCircleIcon : result.status === "skipped" ? HourglassIcon : XCircleIcon}
              </Badge>

              <div>
                <strong>{result.medicineName}</strong>
                {result.status === "added" && <span className="text-green-600">Added successfully</span>}
                {result.status === "skipped" && <span className="text-amber-600">Skipped</span>}
                {result.status === "failed" && (
                  <span className="text-red-600">
                    Failed: {result.error || "Unknown error"}
                  </span>
                )}
              </div>
            </Flex>
          );
        })}
      </Flex>

      {/* Action buttons */}
      <Flex justify="center" space-x-2 mt={3}>
        <Button
          onClick={onViewInventory}
          variant="solid"
          colorScheme="teal"
          size="lg"
        >
          View Inventory
        </Button>
        <Button
          onClick={onScanAnother}
          variant="ghost"
          size="lg"
          colorScheme="gray"
        >
          Scan Another
        </Button>
      </Flex>
    </Card>
  );
}